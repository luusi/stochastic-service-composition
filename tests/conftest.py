"""The conftest.py module."""
import pytest

from stochastic_service_composition.services import Service, build_service_from_transitions
from stochastic_service_composition.types import TransitionFunction
from pytest_lazyfixture import  lazy_fixture


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
        "air_hot": {
            "hot_air_on": "air_hot",
            "air_off": "air_off"
        }
    }
    final_states = {"air_off"}
    initial_state = "air_off"
    return build_service_from_transitions(transitions, initial_state, final_states)


@pytest.fixture
def bathtub_device() -> Service:
    """Build the bathtub device."""
    transitions: TransitionFunction = {
        "empty": {
            "fill_up_buthub": "filled",
        },
        "filled": {
            "empty_buthub": "empty"
        }
    }
    final_states = {"empty"}
    initial_state = "empty"
    return build_service_from_transitions(transitions, initial_state, final_states)


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
    return build_service_from_transitions(transitions, initial_state, final_states)



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
    return build_service_from_transitions(transitions, initial_state, final_states)


@pytest.fixture(params=[
    lazy_fixture('bathroom_heating_device'),
    lazy_fixture('bathtub_device'),
    lazy_fixture('door_device'),
    lazy_fixture('kitchen_exhaust_fan_device'),
])
def all_services(request):
    """Return all test services."""
    return request.param
