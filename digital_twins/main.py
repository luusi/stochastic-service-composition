import argparse
import asyncio
import json
import logging
from pathlib import Path
from typing import Dict

from pprint import pprint

import requests
import websockets as websockets
from mdp_dp_rl.processes.mdp import MDP

from digital_twins.Devices.utils import service_from_json, target_from_json
from digital_twins.constants import ACCESS_BOSCH_IOT_URL, HEADERS
from digital_twins.target_simulator import TargetSimulator
from digital_twins.things_api import config_from_json, ThingsAPI
from stochastic_service_composition.composition import composition_mdp
from stochastic_service_composition.services import Service
from stochastic_service_composition.target import Target, build_target_from_transitions


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


def main(config: str, timeout: int):
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



    """services = []
    for thing_id in THINGS_IDS:
        data = api.get_thing(thing_id)
        assert len(data) == 1
        service: Service = service_from_json(data[0])
        services.append(service)

    # TODO temporary solution, see above
    # data = api.get_thing(TARGET_ID)
    # assert len(data) == 1
    # target: Target = target_from_json(data[0])
    target = get_target()"""

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
        print(f"Sending action to thing {chosen_thing_id}")
        #without timeout the follow function is not blocking
        response = api.send_message_to_thing(chosen_thing_id, target_action, {}, timeout)


        # compute the next system state
        service = services[service_index]
        current_service_state = system_state[service_index]
        next_service_state = service.transition_function[current_service_state][target_action]
        system_state[service_index] = next_service_state

        iteration += 1


if __name__ == "__main__":
    arguments = parser.parse_args()
    main(arguments.config, arguments.timeout)
