"""This module implements the algorithm to compute the system-target MDP."""
from collections import deque
from typing import Deque, Dict, Tuple

from mdp_dp_rl.processes.mdp import MDP

from stochastic_service_composition.services import Service, product
from stochastic_service_composition.target import Target
from stochastic_service_composition.types import Action, State


def composition_mdp(target: Target, *services: Service) -> MDP:
    """
    Compute the composition MDP.

    :param target: the target service.
    :param services: the community of services.
    :return: the composition MDP.
    """
    system_service = product(*services)

    initial_state = 0
    # one action per service (1..n) + the initial action (0)
    actions = set(range(len(services)))
    initial_action = -1
    actions.add(initial_action)

    transition_function: Dict[
        State, Dict[Action, Tuple[Dict[State, float], float]]
    ] = {}

    visited = set()
    to_be_visited = set()
    queue: Deque = deque()

    # add initial transitions
    transition_function[initial_state] = {}
    initial_transition_dist = {}
    symbols_from_initial_state = target.policy[target.initial_state].keys()
    for symbol in symbols_from_initial_state:
        next_state = (system_service.initial_state, target.initial_state, symbol)
        next_prob = target.policy[target.initial_state][symbol]
        initial_transition_dist[next_state] = next_prob
        queue.append(next_state)
        to_be_visited.add(next_state)
    transition_function[initial_state][initial_action] = (initial_transition_dist, 0.0)  # type: ignore

    while len(queue) > 0:
        current_state = queue.popleft()
        to_be_visited.remove(current_state)
        visited.add(current_state)
        current_system_state, current_target_state, current_symbol = current_state

        for (symbol, i), next_system_state in system_service.transition_function[
            current_system_state
        ].items():
            next_transitions = {}
            if symbol in target.transition_function[current_target_state]:
                next_reward = (
                    target.policy[current_target_state][symbol]
                    if (symbol, i)
                    in system_service.transition_function[current_system_state]
                    else 0
                )
                next_target_state = target.transition_function[current_target_state][
                    symbol
                ]
                for next_symbol, next_prob in target.policy[next_target_state].items():
                    next_state = (next_system_state, next_target_state, next_symbol)
                    next_transitions[next_state] = next_prob
                    if next_state not in visited and next_state not in to_be_visited:
                        to_be_visited.add(next_state)
                        queue.append(next_state)
                transition_function.setdefault(current_state, {})[i] = (  # type: ignore
                    next_transitions,
                    next_reward,
                )

    return MDP(transition_function, 0.99)
