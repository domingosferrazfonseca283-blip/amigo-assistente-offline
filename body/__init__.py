"""Corpo universal e abstrações de hardware."""

from .interfaces import Actuator, Body, BodyAdapter, Sense
from .runtime import BodyRuntime

__all__ = ["Actuator", "Body", "BodyAdapter", "BodyRuntime", "Sense"]
