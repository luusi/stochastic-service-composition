from collections import deque
from typing import Set, Dict, Any, Tuple


class Service:
    """A service."""

    def __init__(self, states: Set[Any],
                 actions: Set[Any],
                 final_states: Set[Any],
                 initial_state: Any,
                 transition_function: Dict[Any, Dict[Any, Any]]):
        """
        Initialize the service.

        :param states:
        :param actions:
        :param final_states:
        :param initial_state:
        :param transition_function:
        """
        self.states = states
        self.actions = actions
        self.final_states = final_states
        self.initial_state = initial_state
        self.transition_function = transition_function

        # TODO check


def product(*services: Service) -> Service:
    """Do the product between services."""
    assert len(services) >= 2, "At least two services."

    new_states = set()
    new_final_states = set()
    actions = services[0].actions
    new_initial_state = tuple(service.initial_state for service in services)
    new_transition_function: Dict[Any, Dict[Any, Any]] = {}

    queue = deque()
    queue.append(new_initial_state)
    to_be_visited = {new_initial_state}
    visited = set()
    while len(queue) > 0:
        current_state: Tuple[Any] = queue.popleft()
        to_be_visited.remove(current_state)
        visited.add(current_state)

        new_states.add(current_state)
        if all(component_i in services[i].final_states for i, component_i in enumerate(current_state)):
            new_final_states.add(current_state)

        next_state_template = current_state
        for i in range(len(services)):
            current_service: Service = services[i]
            current_service_state = list(next_state_template[i])
            for a, next_service_state in current_service.transition_function[current_service_state].items():
                next_state = list(next_state_template)
                next_state[i] = next_service_state
                symbol = (a, i)
                new_transition_function.setdefault(current_state, {})[symbol] = tuple(next_state)
                if next_state not in visited and next_state not in to_be_visited:
                    to_be_visited.add(next_state)

    new_service = Service(
        states=new_states,
        actions=actions,
        final_states=new_final_states,
        initial_state=new_initial_state,
        transition_function=new_transition_function,
    )
    return new_service
