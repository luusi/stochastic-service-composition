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

        Both states and action must be of an hashable type.

        :param states: the set of states
        :param actions: the set of actions
        :param final_states: the final states
        :param initial_state: the initial state
        :param transition_function: the transition function
        """
        self.states = states
        self.actions = actions
        self.final_states = final_states
        self.initial_state = initial_state
        self.transition_function = transition_function

    def __post_init__(self):
        """Do post-initialization checks."""
        self._check_number_of_states_at_least_one()
        self._check_number_of_actions_at_least_one()
        self._check_number_of_final_states_at_least_one()
        self._check_initial_state_in_states()
        self._check_all_final_states_in_states()

    def _check_number_of_states_at_least_one(self):
        """Check that the number of states is at least one."""
        assert len(self.states) > 0, "must have at least one state"

    def _check_number_of_actions_at_least_one(self):
        assert len(self.actions) > 0, "must have at least one action"
        """Check that the number of actions is at least one."""

    def _check_number_of_final_states_at_least_one(self):
        """Check that the number of final states is at least one."""
        assert len(self.final_states) > 0, "must have at least one final state"

    def _check_initial_state_in_states(self):
        """Check that the initial state is in the set of states.."""
        assert self.initial_state in self.states, "initial state not in the set of states"

    def _check_all_final_states_in_states(self):
        """Check that all the final states are in the set of states."""
        final_states_not_in_states = {final_state for final_state in self.states if final_state not in self.states}
        assert len(final_states_not_in_states) == 0, f"the following final states are not in the set of states: {final_states_not_in_states}"


def product(*services: Service) -> Service:
    """
    Do the product between services.

    :param services: a list of service instances
    :return: the system service
    """
    assert len(services) >= 2, "at least two services"

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
