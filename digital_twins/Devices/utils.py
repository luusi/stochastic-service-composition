from typing import Dict

from stochastic_service_composition.services import Service, build_service_from_transitions
from stochastic_service_composition.target import Target, build_target_from_transitions


def service_from_json(data: Dict) -> Service:
    """Load a service from its JSON description."""
    attributes = data["attributes"]
    transitions = attributes["transitions"]
    initial_state = attributes["initial_state"]
    final_states = set(attributes["final_states"])
    return build_service_from_transitions(transitions, initial_state, final_states)


def target_from_json(data: Dict) -> Target:
    attributes = data["attributes"]
    transitions = attributes["transitions"]
    initial_state = attributes["initial_state"]
    final_states = set(attributes["final_states"])
    return build_target_from_transitions(transitions, initial_state, final_states)