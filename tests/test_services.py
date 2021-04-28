"""Test the 'services.py' module."""
from stochastic_service_composition.services import Service


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
            cls.transition_function
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
        """Test the getter 'transition_function'."""
        return self.service.transition_function == self.transition_function


def test_initialization_from_transitions(all_services):
    """
    Test the initialization of a service from transitions.

    The test will trigger initialization from the fixtures.
    To see the fixtures, go to 'conftest.py'.
    """
