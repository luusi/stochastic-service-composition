"""Test the 'services.py' module."""
from graphviz import Digraph

from stochastic_service_composition.rendering import service_to_graphviz
from stochastic_service_composition.services import Service, product


class TestInitialization:
    """Test class to test initialization and getters."""

    @classmethod
    def setup(cls):
        cls.states = {"s0", "s1"}
        cls.actions = {"a", "b"}
        cls.final_states = {"s1"}
        cls.initial_state = "s0"
        cls.transition_function = {
            "s0": {"a": "s1"},
            "s1": {"b": "s0"},
        }
        cls.service = Service(
            cls.states,
            cls.actions,
            cls.final_states,
            cls.initial_state,
            cls.transition_function,
        )

    def test_states(self):
        """Test the getter 'states'."""
        return self.service.states == self.states

    def test_actions(self):
        """Test the getter 'actions'."""
        return self.service.actions == self.actions

    def test_final_states(self):
        """Test the getter 'final_states'."""
        return self.service.final_states == self.final_states

    def test_initial_state(self):
        """Test the getter 'initial_state'."""
        return self.service.initial_state == self.initial_state

    def test_transition_function(self):
        """Test the getter 'dynamics_function'."""
        return self.service.transition_function == self.transition_function


def test_initialization_from_transitions(all_services):
    """
    Test the initialization of a service from transitions.

    The test will trigger initialization from the fixtures.
    To see the fixtures, go to 'conftest.py'.
    """


def test_product_one_state(kitchen_exhaust_fan_device, door_device):
    """Test the product between two simple services (one state each)."""
    system_service = product(kitchen_exhaust_fan_device, door_device)

    # since the two operands have only one state, also the
    #  product has one state.
    assert len(system_service.states) == 1
    assert system_service.states == {("unique", "unique")}
    assert system_service.actions == {("vent_kitchen", 0), ("close", 1), ("open", 1)}
    assert system_service.initial_state == ("unique", "unique")
    assert system_service.final_states == {("unique", "unique")}
    assert system_service.transition_function == {
        ("unique", "unique"): {
            ("vent_kitchen", 0): ("unique", "unique"),
            ("open", 1): ("unique", "unique"),
            ("close", 1): ("unique", "unique"),
        }
    }


def test_product_many_states(bathtub_device, door_device):
    """Test the product between two services (more states)."""
    system_service = product(bathtub_device, door_device)

    assert len(system_service.states) == 2
    assert system_service.states == {("empty", "unique"), ("filled", "unique")}
    assert system_service.actions == {
        ("fill_up_bathtub", 0),
        ("empty_bathtub", 0),
        ("open", 1),
        ("close", 1),
    }
    assert system_service.initial_state == ("empty", "unique")
    assert system_service.final_states == {("empty", "unique")}
    assert system_service.transition_function == {
        ("empty", "unique"): {
            ("fill_up_bathtub", 0): ("filled", "unique"),
            ("open", 1): ("empty", "unique"),
            ("close", 1): ("empty", "unique"),
        },
        ("filled", "unique"): {
            ("empty_bathtub", 0): ("empty", "unique"),
            ("open", 1): ("filled", "unique"),
            ("close", 1): ("filled", "unique"),
        },
    }


def test_rendering(all_services):
    """Test the transformation to Digraph."""
    current_service = all_services
    result = service_to_graphviz(current_service)
    assert isinstance(result, Digraph)
