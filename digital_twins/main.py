import argparse
import asyncio
import json
import urllib.parse


import websockets
import logging
from pathlib import Path

from mdp_dp_rl.processes.mdp import MDP

from digital_twins.Devices.utils import service_from_json, target_from_json
from digital_twins.constants import WS_URI
from digital_twins.target_simulator import TargetSimulator
from digital_twins.things_api import config_from_json, ThingsAPI
from stochastic_service_composition.composition import composition_mdp
from stochastic_service_composition.target import Target


def setup_logger():
    """Set up the logger."""
    logger = logging.getLogger("digital_twins")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(fmt="[%(asctime)s][%(name)s][%(levelname)s] %(message)s")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


logger = setup_logger()

parser = argparse.ArgumentParser("main")
parser.add_argument("--config", type=str, default="config.json", help="Path to configuration file (in JSON format).")
parser.add_argument("--timeout", type=int, default=0, help="Timeout to wait message sent correctly.")

# TODO temporary solution. Instead, do a search for available things


#THINGS_IDS = [

 #"com.bosch.services:bathroom_heating_device",
 #"com.bosch.services:bathtub_device",
 #"com.bosch.services:door_device",
 #"com.bosch.services:kitchen_exhaust_fan_device",
 #"com.bosch.services:user_behaviour",
#]

#TARGET_ID = "com.boschservices:target"

"""def get_target():
    # TODO temporary solution; update target definition on Bosch IoT Things
    transition_function = {
        "t0": {
            "hot_air_on": ("t1", 0.6, 5),
            "move_to_kitchen": ("t8", 0.2, 3),
            "open_door_kitchen": ("t7", 0.2, 2),
        },
        "t1": {"fill_up_bathtub": ("t2", 0.7, 4), "hot_air_on": ("t1", 0.3, 2)},
        "t2": {
            "move_to_bathroom": ("t3", 0.5, 3),
            "open_door_bathroom": ("t2", 0.5, 2),
        },
        "t3": {"move_to_bathroom": ("t3", 0.2, 4), "wash": ("t4", 0.8, 8)},
        "t4": {"move_to_bedroom": ("t5", 1.0, 10)},
        "t5": {"empty_bathtub": ("t6", 0.9, 7), "move_to_bedroom": ("t5", 0.1, 3)},
        "t6": {"air_off": ("t7", 1.0, 10)},
        "t7": {"move_to_kitchen": ("t8", 0.5, 5), "open_door_kitchen": ("t7", 0.5, 4)},
        "t8": {
            "cook_eggs": ("t9", 0.6, 7),
            "move_to_kitchen": ("t8", 0.2, 5),
            "prepare_tea": ("t0", 0.2, 2),
        },
        "t9": {"no_op": ("t0", 0.8, 1), "vent_kitchen": ("t9", 0.2, 1)},
    }

    initial_state = "t0"
    final_states = {"t0"}

    return build_target_from_transitions(
        transition_function, initial_state, final_states
    )"""


async def main(config: str, timeout: int):

    """Run the main."""
    services = []
    service_ids = []
    configuration = config_from_json(Path(config))
    api = ThingsAPI(configuration)
    data = api.search_services("")
    for element in data:
        service = service_from_json(element)
        services.append(service)

        service_ids.append(element["thingId"])


    data = api.search_targets("")
    assert len(data) == 1
    target: Target = target_from_json(data[0])

    print("Opening websocket endpoint...")
    ws_uri = "wss://things.eu-1.bosch-iot-suite.com/ws/2"
    async with websockets.connect(ws_uri, extra_headers=websockets.http.Headers({
                                      'Authorization': 'Bearer ' + api.get_token()
                                  })) as websocket:
        print("Collecting problem data...")

        mdp: MDP = composition_mdp(target, *services)
        orchestrator_policy = mdp.get_optimal_policy()
        target_simulator = TargetSimulator(target)
        system_state = [service.initial_state for service in services]

        iteration = 0
        while True:
            current_target_state = target_simulator.current_state
            target_action = target_simulator.sample_action_and_update_state()
            print(f"Iteration: {iteration}, target action: {target_action}")
            current_state = (tuple(system_state), current_target_state, target_action)

            orchestrator_choice = orchestrator_policy.get_action_for_state(current_state)
            if orchestrator_choice == "undefined":
                print(f"Execution failed: no service can execute {target_action} in system state {system_state}")
                break
            # send_action_to_service
            service_index = orchestrator_choice
            chosen_thing_id = service_ids[service_index]
            event_cmd = "START-SEND-EVENTS?filter="
            event_cmd += '(eq(thingId,"' + chosen_thing_id + \
                         '"))'
            print("EVENT_CMD: ", event_cmd)
            event_cmd = urllib.parse.quote(event_cmd, safe='')
            print(f"Sending action to thing {chosen_thing_id}: {event_cmd}")
            await websocket.send(event_cmd)
            print("Listening to events originating from " + chosen_thing_id)
            message_receive = await websocket.recv()
            print("Message received: ", message_receive)
            if message_receive != "START-SEND-EVENTS:ACK":
                raise Exception("Ack not received")

            print("Sending message to thing: ", chosen_thing_id, target_action, timeout)
            response = api.send_message_to_thing(chosen_thing_id, target_action, {}, timeout)
            print(f"Got response: {response}")
            print("Waiting for update from websocket...")
            message_receive = await websocket.recv()
            print(f"Update after change: {message_receive}")
            json_message = json.loads(message_receive)
            next_service_state = json_message["value"]

            # compute the next system state

            # TODO: TEMPORARY SOLUTION
            # service = services[service_index]
            # current_service_state = system_state[service_index]
            # next_service_states, reward = service.transition_function[current_service_state][target_action]
            # states, probabilities = zip(*next_service_states.items())
            # next_service_state = random.choices(states, probabilities)[0]

            system_state[service_index] = next_service_state
            await websocket.send("STOP-SEND-EVENTS")
            await websocket.recv()
            iteration += 1


if __name__ == "__main__":
    arguments = parser.parse_args()
    result = asyncio.get_event_loop().run_until_complete(main(arguments.config, arguments.timeout))
