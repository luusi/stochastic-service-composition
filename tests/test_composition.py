"""This module contains the tests for the target.py module."""
from graphviz import Digraph
from mdp_dp_rl.processes.mdp import MDP

from stochastic_service_composition.composition import composition_mdp
from stochastic_service_composition.rendering import target_to_graphviz
from stochastic_service_composition.target import Target


def test_composition(
    target_service,
    bathroom_heating_device,
    bathtub_device,
    kitchen_door_device,
    bathroom_door_device,
    kitchen_exhaust_fan_device,
    user_behaviour,
):
    """Test a composition example."""
    services = [
        bathroom_heating_device,
        bathtub_device,
        kitchen_door_device,
        bathroom_door_device,
        kitchen_exhaust_fan_device,
        user_behaviour,
    ]
    mdp = composition_mdp(target_service, *services)
    assert isinstance(mdp, MDP)
