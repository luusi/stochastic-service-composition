"""
This module contains the main type definitions.

In particular:
- State is the type of state; we require the
"""
from typing import Any, Dict, Hashable

State = Hashable
Action = Any
TransitionFunction = Dict[State, Dict[Action, State]]
