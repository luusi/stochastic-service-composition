import argparse
import asyncio
import json
import urllib.parse


import websockets
import logging
from pathlib import Path

from mdp_dp_rl.processes.mdp import MDP

from digital_twins.Devices.utils import service_from_json, target_from_json
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
    target_thing_id = data[0]["thingId"]

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

        event_cmd = "START-SEND-EVENTS"
        print("EVENT_CMD: ", event_cmd)
        event_cmd = urllib.parse.quote(event_cmd, safe='')
        await websocket.send(event_cmd)
        print("Listening to events originating")
        message_receive = await websocket.recv()
        print("Message received: ", message_receive)
        if message_receive != "START-SEND-EVENTS:ACK":
            raise Exception("Ack not received")

        while True:
            # waiting for target action
            print("Waiting for messages from target...")
            target_message = await websocket.recv()
            target_message_json = json.loads(target_message)
            #assert target_message["thingId"] == target_thing_id, "not a message from the target"
            target_action = target_message_json["value"]
            current_target_state = target_simulator.current_state
            target_simulator.update_state(target_action)
            print(f"Iteration: {iteration}, target action: {target_action}")
            current_state = (tuple(system_state), current_target_state, target_action)

            orchestrator_choice = orchestrator_policy.get_action_for_state(current_state)
            if orchestrator_choice == "undefined":
                print(f"Execution failed: no service can execute {target_action} in system state {system_state}")
                break
            # send_action_to_service
            service_index = orchestrator_choice
            chosen_thing_id = service_ids[service_index]
            print("Sending message to thing: ", chosen_thing_id, target_action, timeout)
            response = api.send_message_to_thing(chosen_thing_id, target_action, {}, timeout)
            print(f"Got response")
            print("Waiting for update from websocket...")
            message_receive = await websocket.recv()
            print(f"Update after change: {message_receive}")
            json_message = json.loads(message_receive)
            # assert json_message["thingId"] == chosen_thing_id, "not the right thing id"
            next_service_state = json_message["value"]
            # compute the next system state
            system_state[service_index] = next_service_state

            # send "DONE" to target
            response = api.send_message_to_thing(target_thing_id, "done", {}, timeout)
            iteration += 1


if __name__ == "__main__":
    arguments = parser.parse_args()
    result = asyncio.get_event_loop().run_until_complete(main(arguments.config, arguments.timeout))
