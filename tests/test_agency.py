from __future__ import annotations

import unittest

from app.action_system import ActionRequest, ActionSystem
from app.agency import ActionCapability, ActionRisk, PermissionMode
from app.goals import GoalManager
from app.agency import AgencyEngine
from app.initiative import InitiativeEngine, InitiativePolicy


class Handler:
    def execute(self, action: str, payload: dict):
        return {"action": action, "payload": payload}


class AgencyTests(unittest.TestCase):
    def test_confirmation_is_required(self):
        system = ActionSystem()
        system.register(ActionCapability(
            "send_message", "Enviar mensagem", ActionRisk.MEDIUM, PermissionMode.CONFIRM
        ), Handler())
        with self.assertRaises(PermissionError):
            system.execute(ActionRequest("send_message", {"text": "olá"}))
        result = system.execute(ActionRequest("send_message", {"text": "olá"}, confirmed=True))
        self.assertEqual(result["action"], "send_message")

    def test_initiative_requires_high_priority_goal(self):
        goals = GoalManager()
        agency = AgencyEngine()
        engine = InitiativeEngine(goals, agency, InitiativePolicy(cooldown_seconds=0))
        self.assertIsNone(engine.evaluate())
        goal = goals.add("Objetivo importante", priority=0.9)
        initiative = engine.evaluate("teste")
        self.assertIsNotNone(initiative)
        self.assertEqual(initiative.goal_id, goal.id)
        self.assertTrue(initiative.requires_confirmation)

    def test_disabled_capability_cannot_execute(self):
        system = ActionSystem()
        system.register(ActionCapability(
            "danger", "ação bloqueada", ActionRisk.HIGH, PermissionMode.DENY
        ), Handler())
        with self.assertRaises(PermissionError):
            system.execute(ActionRequest("danger", {}))


if __name__ == "__main__":
    unittest.main()
