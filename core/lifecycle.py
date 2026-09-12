from __future__ import annotations

from enum import Enum


class Lifecycle(str, Enum):
    NEW = "new"
    AWAKE = "awake"
    IDLE = "idle"
    SLEEPING = "sleeping"
    OFFLINE = "offline"
    SHUTDOWN = "shutdown"


_TRANSITIONS = {
    Lifecycle.NEW: {Lifecycle.AWAKE, Lifecycle.SHUTDOWN},
    Lifecycle.AWAKE: {Lifecycle.IDLE, Lifecycle.SLEEPING, Lifecycle.OFFLINE, Lifecycle.SHUTDOWN},
    Lifecycle.IDLE: {Lifecycle.AWAKE, Lifecycle.SLEEPING, Lifecycle.OFFLINE, Lifecycle.SHUTDOWN},
    Lifecycle.SLEEPING: {Lifecycle.AWAKE, Lifecycle.OFFLINE, Lifecycle.SHUTDOWN},
    Lifecycle.OFFLINE: {Lifecycle.AWAKE, Lifecycle.SLEEPING, Lifecycle.SHUTDOWN},
    Lifecycle.SHUTDOWN: set(),
}


class LifecycleController:
    def __init__(self, state: Lifecycle = Lifecycle.NEW) -> None:
        self.state = state

    def transition(self, target: Lifecycle) -> Lifecycle:
        if target == self.state:
            return self.state
        if target not in _TRANSITIONS[self.state]:
            raise ValueError(f"Transição inválida: {self.state.value} -> {target.value}")
        self.state = target
        return self.state
