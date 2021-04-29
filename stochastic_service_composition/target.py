"""Represent a target service."""
from typing import Dict, Set

from stochastic_service_composition.services import (
    Service,
    build_service_from_transitions,
)
from stochastic_service_composition.types import Action, State, TransitionFunction


class Target(Service):
    """Represent a target service."""

    def __init__(
        self,
        states: Set[State],
        actions: Set[Action],
        final_states: Set[State],
        initial_state: State,
        transition_function: Dict[State, Dict[Action, State]],
        policy: Dict[State, Dict[Action, float]],
        reward: Dict[State, Dict[Action, float]],
    ):
        """
        Initialize the target service.

        :param states: the set of states
        :param actions: the set of actions
        :param final_states: the final states
        :param initial_state: the initial state
        :param transition_function: the transition function
        :param policy: the user's policy
        :param reward: the reward function
        """
        super().__init__(
            states, actions, final_states, initial_state, transition_function
        )
        self.policy = policy
        self.reward = reward

    def __post_init__(self):
        """Run post-initialization checks."""
        self._check_policy_consistency()
        self._check_reward_consistency()

    def _check_policy_consistency(self):
        """
        Check the consistency of the policy.

        In particular:
        - check that all the states belong to the state space of the service
        - check that all teh actions belong to the action space of the service
        - check that the probabilities are between 0 and 1
        - check that the policy, given a state, is a probability distribution
        """
        for state, prob_by_action in self.policy.items():
            assert state in self.states, f"state {state} not in the set of states"
            total_probability = 0.0
            for action, probability in prob_by_action.items():
                assert (
                    action in self.actions
                ), f"action {action} not in the set of actions"
                assert (
                    0 <= probability <= 1.0
                ), f"probability {probability} is not in the interval [0.0, 1.0]"
                assert (
                    action in self.transition_function.get(state, {}).keys()
                ), f"action {action} cannot be taken in state {state}"
                total_probability += probability
            assert total_probability == 1.0, (
                f"probability from state {state} is not a probability distribution; "
                f"expected sum 1.0, got {total_probability}"
            )

    def _check_reward_consistency(self):
        """
        Check the reward function consistency.

        In particular:
        - check that all the states are in the state space of the service
        """
        for state, reward_by_action in self.reward:
            assert state in self.states, f"state {state} not in the set of states"
            for action, reward in reward_by_action.items():
                assert (
                    action in self.actions
                ), f"action {action} is not in the set of actions"
                assert (
                    action in self.transition_function.get(state, {}).keys()
                ), f"action {action} cannot be taken in state {state}"
                assert isinstance(
                    reward, float
                ), f"reward {reward} is not an instance of float"


def build_target_from_transitions(
    transition_function: TransitionFunction,
    initial_state: State,
    final_states: Set[State],
    policy: Dict[State, Dict[Action, float]],
    reward: Dict[State, Dict[Action, float]],
) -> Target:
    """
    Initialize a service from transitions, initial state and final states.

    The set of states and the set of actions are parsed from the transition function.
    This will guarantee that all the states are reachable.

    :param transition_function: the transition function
    :param initial_state: the initial state
    :param final_states: the final states
    :return: the service
    """
    service = build_service_from_transitions(
        transition_function, initial_state, final_states
    )
    target = Target(
        service.states,
        service.actions,
        service.final_states,
        service.initial_state,
        service.transition_function,
        policy,
        reward,
    )
    return target
