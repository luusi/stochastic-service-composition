
from stochastic_service_composition.target import Target
import random


class TargetSimulator:
    """Simulate a target."""

    def __init__(self, target: Target):
        """Initialize the simulator."""
        self.target = target

        self._current_state = self.target.initial_state

    @property
    def current_state(self):
        return self._current_state

    def reset(self):
        """Reset the target to its initial state."""
        self._current_state = self.target.initial_state

    def sample_action_and_update_state(self):
        """Sample the next action and update the state."""
        transitions_from_state = self.target.transition_function[self._current_state]
        action_to_probability = self.target.policy[self._current_state]
        actions, probabilities = zip(*action_to_probability.items())
        sampled_action = random.choices(actions, probabilities)[0]
        next_state = transitions_from_state[sampled_action]
        self._current_state = next_state
        return sampled_action
