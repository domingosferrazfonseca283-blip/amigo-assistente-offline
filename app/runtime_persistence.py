from __future__ import annotations

from typing import Any


def _restore_dataclass_list(container: list, cls: Any, values: list[dict[str, Any]]) -> None:
    from dataclasses import fields
    allowed = {item.name for item in fields(cls)}
    container.clear()
    for raw in values:
        container.append(cls(**{key: value for key, value in dict(raw).items() if key in allowed}))


def restore_runtime_core(runtime: Any, snapshot: dict[str, Any]) -> None:
    """Reconstrói o estado persistente do CognitiveRuntime, incluindo memória cognitiva."""
    from .agency import ActionCapability, ActionRisk, PermissionMode, Plan, PlanStep, Initiative
    from .autonomy import AutonomyDecision, AutonomyLevel, AutonomyPolicy, Choice
    from .cognitive_state import NoemiaState
    from .decision_learning import DecisionOutcome, LearnedPreference
    from .episodic_memory import Episode
    from .expectation_engine import Expectation, ExpectationResult, ExpectationStatus
    from .global_workspace import WorkspaceFocus, WorkspaceItem, WorkspaceKind
    from .memory_association import MemoryLink, MemoryNode
    from .noemia_being import NoemiaBeing
    from .semantic_memory import Belief, BeliefKind
    from .state_change import StateChange, StateSnapshot, Permanence
    from .temporal_memory import TimelineEvent, TemporalLink, TemporalRelation
    from .world_model import WorldModel

    runtime.state = NoemiaState.from_dict(dict(snapshot.get("state", {})))
    runtime.being = NoemiaBeing.restore(dict(snapshot.get("being", {})))
    runtime.world = WorldModel.from_dict(list(snapshot.get("world", [])))
    runtime.relationship.restore(snapshot.get("relationship"))
    runtime.affect.state = runtime.state.affect

    runtime.goals.goals.clear()
    from .goals import Goal, GoalStatus
    for raw in snapshot.get("goals", []):
        data = dict(raw)
        data["status"] = GoalStatus(data.get("status", GoalStatus.ACTIVE))
        goal = Goal(**data)
        runtime.goals.goals[goal.id] = goal
    runtime.state.active_goals = [goal.id for goal in runtime.goals.active()]

    _restore_dataclass_list(runtime.episodic.episodes, Episode, snapshot.get("episodic_memory", []))

    runtime.semantic.beliefs.clear()
    for raw in snapshot.get("semantic_memory", []):
        data = dict(raw)
        data["kind"] = BeliefKind(data.get("kind", BeliefKind.INFERRED))
        belief = Belief(**data)
        runtime.semantic.beliefs[belief.id] = belief

    associative = snapshot.get("associative_memory", {})
    runtime.associations.nodes.clear()
    runtime.associations.links.clear()
    for raw in associative.get("nodes", []):
        data = dict(raw)
        data["tags"] = set(data.get("tags", []))
        node = MemoryNode(**data)
        runtime.associations.nodes[node.id] = node
    for raw in associative.get("links", []):
        runtime.associations.links.append(MemoryLink(**dict(raw)))

    temporal = snapshot.get("temporal_memory", {})
    runtime.timeline.events.clear()
    runtime.timeline.links.clear()
    for raw in temporal.get("events", []):
        runtime.timeline.events.append(TimelineEvent(**dict(raw)))
    for raw in temporal.get("links", []):
        data = dict(raw)
        data["relation"] = TemporalRelation(data["relation"])
        runtime.timeline.links.append(TemporalLink(**data))

    history = snapshot.get("state_history", {})
    runtime.state_history.snapshots.clear()
    runtime.state_history.changes.clear()
    runtime.state_history._current.clear()
    for raw in history.get("snapshots", []):
        item = StateSnapshot(**dict(raw))
        runtime.state_history.snapshots.append(item)
        runtime.state_history._current[(item.subject, item.property)] = item
    for raw in history.get("changes", []):
        data = dict(raw)
        data["permanence"] = Permanence(data.get("permanence", Permanence.UNKNOWN))
        runtime.state_history.changes.append(StateChange(**data))

    runtime.agency.plans.clear()
    for goal_id, raw in snapshot.get("plans", {}).items():
        steps = []
        for step in raw.get("steps", []):
            data = dict(step)
            data["risk"] = ActionRisk(data.get("risk", ActionRisk.LOW))
            steps.append(PlanStep(**data))
        runtime.agency.plans[goal_id] = Plan(goal_id, steps, float(raw.get("confidence", 0.5)))

    for name, raw in snapshot.get("capabilities", {}).items():
        data = dict(raw)
        data["risk"] = ActionRisk(data.get("risk", ActionRisk.LOW))
        data["permission"] = PermissionMode(data.get("permission", PermissionMode.CONFIRM))
        runtime.agency.capabilities[name] = ActionCapability(**data)

    initiative = snapshot.get("initiative", {})
    runtime.initiative.policy.enabled = bool(initiative.get("enabled", runtime.initiative.policy.enabled))
    runtime.initiative.pending = [Initiative(**dict(item)) for item in initiative.get("pending", [])]

    autonomy = snapshot.get("autonomy", {})
    policy = autonomy.get("policy", {})
    runtime.autonomy.policy = AutonomyPolicy(
        level=AutonomyLevel(policy.get("level", runtime.autonomy.policy.level)),
        allow_background_reasoning=bool(policy.get("allow_background_reasoning", True)),
        allow_self_initiated_goals=bool(policy.get("allow_self_initiated_goals", True)),
        require_confirmation_for_external_actions=bool(policy.get("require_confirmation_for_external_actions", True)),
        max_action_risk=str(policy.get("max_action_risk", "low")),
    )
    runtime.autonomy.decisions.clear()
    for raw in autonomy.get("decisions", []):
        data = dict(raw)
        data["chosen"] = Choice(**data["chosen"]) if data.get("chosen") else None
        data["alternatives"] = [Choice(**item) for item in data.get("alternatives", [])]
        data["autonomy_level"] = AutonomyLevel(data.get("autonomy_level", AutonomyLevel.CHOOSE))
        runtime.autonomy.decisions.append(AutonomyDecision(**data))

    learning = snapshot.get("decision_learning", {})
    runtime.decision_learning.outcomes.clear()
    runtime.decision_learning.preferences.clear()
    for raw in learning.get("outcomes", []):
        runtime.decision_learning.outcomes.append(DecisionOutcome(**dict(raw)))
    for raw in learning.get("preferences", []):
        item = LearnedPreference(**dict(raw))
        runtime.decision_learning.preferences[f"{item.key}::{item.option}"] = item

    expectations = snapshot.get("expectations", {})
    runtime.expectations.expectations.clear()
    runtime.expectations.results.clear()
    for raw in expectations.get("expectations", []):
        data = dict(raw)
        data["status"] = ExpectationStatus(data.get("status", ExpectationStatus.ACTIVE))
        runtime.expectations.expectations.append(Expectation(**data))
    for raw in expectations.get("results", []):
        data = dict(raw)
        data["status"] = ExpectationStatus(data.get("status", ExpectationStatus.ACTIVE))
        runtime.expectations.results.append(ExpectationResult(**data))

    workspace = snapshot.get("global_workspace", {})
    runtime.workspace.capacity = int(workspace.get("capacity", runtime.workspace.capacity))
    runtime.workspace.focus_capacity = int(workspace.get("focus_capacity", runtime.workspace.focus_capacity))
    runtime.workspace.items.clear()
    runtime.workspace.focus.clear()
    runtime.workspace.cycle_count = int(workspace.get("cycle_count", 0))
    for raw in workspace.get("items", []):
        data = dict(raw)
        data["kind"] = WorkspaceKind(data["kind"])
        runtime.workspace.items.append(WorkspaceItem(**data))
    for raw in workspace.get("focus", []):
        data = dict(raw)
        data["kind"] = WorkspaceKind(data["kind"])
        runtime.workspace.focus.append(WorkspaceFocus(**data))
