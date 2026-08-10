#!/usr/bin/env python3
"""Generate and validate the version-pinned initial Project Status v2 bootstrap record."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

AUTHORITY = "armpitpete/merrin-project-controls@7bc8b7f5ef921851ad163093f089d28d8128bf6c"
STAGES = (
    "designed",
    "implemented",
    "automated-checks",
    "independent-review",
    "merged",
    "deployed",
    "live-behaviour",
    "human-acceptance",
)
STATUS_TO_STAGE = {
    "designed": "designed",
    "implemented": "implemented",
    "automated-checks-passed": "automated-checks",
    "independently-reviewed": "independent-review",
    "merged": "merged",
    "deployed": "deployed",
    "live-behaviour-verified": "live-behaviour",
    "human-acceptance-received": "human-acceptance",
}
REQUIRED_ENVIRONMENTS = {
    "designed": "accepted project authority",
    "implemented": "exact implementation commit",
    "automated-checks": "exact-head automated checks",
    "independent-review": "exact-head independent review",
    "merged": "default-branch commit",
    "deployed": "declared deployment environment",
    "live-behaviour": "actual live environment",
    "human-acceptance": "declared human acceptance environment",
}
FORBIDDEN_FRAGMENTS = (
    "I:\\",
    "C:\\",
    "GH_TOKEN",
    "GITHUB_TOKEN",
    "BEGIN PRIVATE KEY",
    "sk-",
    "private inventory",
)


class StatusError(ValueError):
    """Raised when the bootstrap Project Status v2 record is not truthful."""


def initial_record(repository: str, project_name: str) -> dict[str, Any]:
    stages = [
        {
            "stage": stage,
            "required": True,
            "required_environment": REQUIRED_ENVIRONMENTS[stage],
            "result": "INSUFFICIENT",
            "relationship": "missing",
            "evidence": [],
            "limitations": [f"No direct {stage} evidence has been recorded yet."],
        }
        for stage in STAGES
    ]
    return {
        "project": repository,
        "finish_line": f"Define and evidence the first bounded finish line for {project_name}.",
        "percentage_complete": {
            "estimate": 0,
            "confidence": "high",
            "evidence": [
                "Only repository bootstrap has occurred; project work is not counted as complete."
            ],
            "remaining_work": [
                "Accept a bounded project authority and record direct lifecycle evidence."
            ],
            "blockers": [],
        },
        "completion_likelihood": {
            "assessment": "possible",
            "confidence": "low",
            "reasons": [
                "The project has been created, but its first accepted finish line is not yet evidenced."
            ],
        },
        "lifecycle_status": {
            "claimed": "designed",
            "verified": "insufficient",
            "authority": AUTHORITY,
            "limitations": [
                "Generated bootstrap fixture; not implementation, deployment, live-behaviour or acceptance evidence."
            ],
            "stages": stages,
        },
        "next_bounded_action": (
            "Assess and inventory source material without modifying it, then accept one bounded project authority."
        ),
    }


def _stage_map(record: dict[str, Any]) -> dict[str, dict[str, Any]]:
    lifecycle = record.get("lifecycle_status")
    if not isinstance(lifecycle, dict):
        raise StatusError("lifecycle_status must be an object")
    raw_stages = lifecycle.get("stages")
    if not isinstance(raw_stages, list) or len(raw_stages) != len(STAGES):
        raise StatusError("all eight bootstrap lifecycle stages must be present")

    stages: dict[str, dict[str, Any]] = {}
    for item in raw_stages:
        if not isinstance(item, dict):
            raise StatusError("every lifecycle stage must be an object")
        name = item.get("stage")
        if name not in STAGES or name in stages:
            raise StatusError("bootstrap lifecycle stages must be unique canonical stages")
        stages[name] = item

    if set(stages) != set(STAGES):
        raise StatusError("all eight bootstrap lifecycle stages must be present")
    return stages


def derive_verified(record: dict[str, Any]) -> str:
    stages = _stage_map(record)
    lifecycle = record["lifecycle_status"]
    claimed = lifecycle.get("claimed")
    if claimed not in set(STATUS_TO_STAGE) | {"complete"}:
        raise StatusError(f"unsupported lifecycle claim: {claimed!r}")

    relevant = (
        list(STAGES)
        if claimed == "complete"
        else list(STAGES[: STAGES.index(STATUS_TO_STAGE[claimed]) + 1])
    )
    if any(stages[name].get("result") == "FAIL" for name in relevant):
        return "failed"
    if all(
        stages[name].get("result") == "PASS"
        and stages[name].get("relationship") == "direct"
        and stages[name].get("observed_environment")
        == stages[name].get("required_environment")
        and isinstance(stages[name].get("evidence"), list)
        and len(stages[name]["evidence"]) > 0
        for name in relevant
    ):
        return "complete" if claimed == "complete" else claimed
    return "insufficient"


def validate(record: Any) -> None:
    if not isinstance(record, dict):
        raise StatusError("project status must be an object")

    required_fields = {
        "project",
        "finish_line",
        "percentage_complete",
        "completion_likelihood",
        "lifecycle_status",
        "next_bounded_action",
    }
    missing = sorted(required_fields - set(record))
    if missing:
        raise StatusError("missing fields: " + ", ".join(missing))

    percentage = record.get("percentage_complete")
    if not isinstance(percentage, dict):
        raise StatusError("percentage_complete must be an object")
    estimate = percentage.get("estimate")
    if (
        not isinstance(estimate, (int, float))
        or isinstance(estimate, bool)
        or not 0 <= estimate <= 100
    ):
        raise StatusError("percentage_complete.estimate must be numeric from 0 to 100")

    lifecycle = record.get("lifecycle_status")
    if not isinstance(lifecycle, dict):
        raise StatusError("lifecycle_status must be an object")
    if lifecycle.get("authority") != AUTHORITY:
        raise StatusError("project status authority is not the pinned shared control")
    claimed = lifecycle.get("claimed")
    if claimed not in set(STATUS_TO_STAGE) | {"complete"}:
        raise StatusError("unsupported lifecycle claim")

    stages = _stage_map(record)
    for name in STAGES:
        item = stages[name]
        if item.get("required") is not True:
            raise StatusError(f"bootstrap lifecycle stage {name} must remain required")
        if item.get("required_environment") != REQUIRED_ENVIRONMENTS[name]:
            raise StatusError(
                f"{name} required environment does not match the pinned bootstrap contract"
            )

        result = item.get("result")
        relationship = item.get("relationship")
        evidence = item.get("evidence")
        if not isinstance(evidence, list):
            raise StatusError(f"{name} evidence must be an array")

        if result in {"PASS", "FAIL"}:
            if relationship != "direct" or not evidence:
                raise StatusError(f"{name} PASS/FAIL requires direct evidence")
            if item.get("observed_environment") != item.get("required_environment"):
                raise StatusError(f"{name} PASS/FAIL must exercise the required environment")
        elif result == "INSUFFICIENT":
            if relationship not in {"direct", "proxy", "missing"}:
                raise StatusError(f"{name} INSUFFICIENT relationship is invalid")
        else:
            raise StatusError(f"{name} bootstrap stage must be PASS, FAIL or INSUFFICIENT")

    expected = derive_verified(record)
    if lifecycle.get("verified") != expected:
        raise StatusError(f"lifecycle_status.verified must be {expected!r}")

    rendered = json.dumps(record, sort_keys=True)
    for fragment in FORBIDDEN_FRAGMENTS:
        if fragment.lower() in rendered.lower():
            raise StatusError(f"privacy-sensitive fragment present: {fragment}")


def write_initial_record(path: Path, repository: str, project_name: str) -> None:
    record = initial_record(repository, project_name)
    validate(record)
    path.write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def load_and_validate(path: Path) -> None:
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise StatusError(f"cannot read project status: {exc}") from exc
    validate(record)
