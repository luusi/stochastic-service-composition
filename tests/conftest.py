"""The conftest.py module."""
import pytest
from pytest_lazyfixture import lazy_fixture

from stochastic_service_composition.services import (
    Service,
    build_service_from_transitions,
)
from stochastic_service_composition.target import Target, build_target_from_transitions
from stochastic_service_composition.types import TransitionFunction


@pytest.fixture
def bathroom_heating_device() -> Service:
    """Build the bathroom heating device."""
    transitions: TransitionFunction = {
        "air_cold": {
            "cold_air_on": "air_cold",
            "air_off": "air_off",
        },
        "air_off": {
            "cold_air_on": "air_cold",
            "hot_air_on": "air_hot",
        },
        "air_hot": {"hot_air_on": "air_hot", "air_off": "air_off"},
    }
    final_states = {"air_off"}
    initial_state = "air_off"
    return build_service_from_transitions(transitions, initial_state, final_states)  # type: ignore


@pytest.fixture
def bathtub_device() -> Service:
    """Build the bathtub device."""
    transitions: TransitionFunction = {
        "empty": {
            "fill_up_buthub": "filled",
        },
        "filled": {"empty_buthub": "empty"},
    }
    final_states = {"empty"}
    initial_state = "empty"
    return build_service_from_transitions(transitions, initial_state, final_states)  # type: ignore


@pytest.fixture
def door_device() -> Service:
    """Build the door device."""
    transitions: TransitionFunction = {
        "unique": {
            "open": "unique",
            "close": "unique",
        },
    }
    final_states = {"unique"}
    initial_state = "unique"
    return build_service_from_transitions(transitions, initial_state, final_states)  # type: ignore


@pytest.fixture
def kitchen_exhaust_fan_device() -> Service:
    """Build the kitchen exhaust fan device."""
    transitions: TransitionFunction = {
        "unique": {
            "vent_kitchen": "unique",
        },
    }
    final_states = {"unique"}
    initial_state = "unique"
    return build_service_from_transitions(transitions, initial_state, final_states)  # type: ignore


@pytest.fixture
def user_behaviour() -> Service:
    """It is the user behaviour service."""
    transitions: TransitionFunction = {
        "s0": {
            "move_to_bedroom": "s0",
            "move_to_bathroom": "s1",
            "move_to_kitchen": "s3",
        },
        "s1": {
            "move_to_bathroom": "s1",
            "wash": "s2",
        },
        "s2": {
            "move_to_bedroom": "s0",
        },
        "s3": {
            "move_to_kitchen": "s3",
            "cook_eggs": "s0",
            "prepare_tea": "s0",
        },
    }
    initial_state = "s0"
    final_states = {"s0"}
    return build_service_from_transitions(transitions, initial_state, final_states)  # type: ignore


@pytest.fixture(
    params=[
        lazy_fixture("bathroom_heating_device"),
        lazy_fixture("bathtub_device"),
        lazy_fixture("door_device"),
        lazy_fixture("kitchen_exhaust_fan_device"),
        lazy_fixture("user_behaviour"),
    ]
)
def all_services(request):
    """Return all test services."""
    return request.param


@pytest.fixture()
def target_service():
    """Build the target service."""
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
    )
