#!/usr/bin/env python3
"""Generate the version-pinned initial Project Status v2 bootstrap profile.

This module is deliberately not a replacement for the canonical Project Status v2
schema or validator in armpitpete/merrin-project-controls. It owns only the fixed
initial profile emitted by project-template and the exact authority pointer used by
later project status records.
"""

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
    """Raised when the template bootstrap profile or authority pointer is invalid."""


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
                "Generated bootstrap profile; not implementation, deployment, live-behaviour or acceptance evidence."
            ],
            "stages": stages,
        },
        "next_bounded_action": (
            "Assess and inventory source material without modifying it, then accept one bounded project authority."
        ),
    }


def _forbid_private_fragments(record: Any) -> None:
    rendered = json.dumps(record, sort_keys=True)
    for fragment in FORBIDDEN_FRAGMENTS:
        if fragment.lower() in rendered.lower():
            raise StatusError(f"privacy-sensitive fragment present: {fragment}")


def validate_initial_bootstrap(record: Any) -> None:
    """Validate only the fixed profile that this template itself generates.

    This is intentionally narrower than the canonical Project Status v2 validator.
    It prevents the template bootstrap from inventing progress or relaxing stages;
    it does not adjudicate later project lifecycle records.
    """

    if not isinstance(record, dict):
        raise StatusError("bootstrap project status must be an object")

    expected_top = {
        "project",
        "finish_line",
        "percentage_complete",
        "completion_likelihood",
        "lifecycle_status",
        "next_bounded_action",
    }
    if set(record) != expected_top:
        raise StatusError("bootstrap project status has unexpected or missing top-level fields")

    if not isinstance(record.get("project"), str) or not record["project"].strip():
        raise StatusError("bootstrap project identity must be non-empty")
    if not isinstance(record.get("finish_line"), str) or not record["finish_line"].strip():
        raise StatusError("bootstrap finish line must be non-empty")
    if not isinstance(record.get("next_bounded_action"), str) or not record["next_bounded_action"].strip():
        raise StatusError("bootstrap next bounded action must be non-empty")

    progress = record.get("percentage_complete")
    if not isinstance(progress, dict) or progress.get("estimate") != 0:
        raise StatusError("bootstrap planning estimate must remain exactly 0")
    if progress.get("confidence") != "high":
        raise StatusError("bootstrap planning confidence must remain high")

    likelihood = record.get("completion_likelihood")
    if not isinstance(likelihood, dict):
        raise StatusError("bootstrap completion likelihood must be an object")
    if likelihood.get("assessment") != "possible" or likelihood.get("confidence") != "low":
        raise StatusError("bootstrap completion likelihood must remain possible / low-confidence")

    lifecycle = record.get("lifecycle_status")
    if not isinstance(lifecycle, dict):
        raise StatusError("bootstrap lifecycle_status must be an object")
    if lifecycle.get("authority") != AUTHORITY:
        raise StatusError("bootstrap lifecycle authority is not the exact shared-control pin")
    if lifecycle.get("claimed") != "designed" or lifecycle.get("verified") != "insufficient":
        raise StatusError("bootstrap cannot claim or verify lifecycle progress")

    raw_stages = lifecycle.get("stages")
    if not isinstance(raw_stages, list) or len(raw_stages) != len(STAGES):
        raise StatusError("bootstrap must contain exactly eight lifecycle stages")
    if [item.get("stage") for item in raw_stages if isinstance(item, dict)] != list(STAGES):
        raise StatusError("bootstrap lifecycle stages must appear once in canonical order")

    for item, stage in zip(raw_stages, STAGES):
        if not isinstance(item, dict):
            raise StatusError("bootstrap lifecycle stage must be an object")
        if item.get("required") is not True:
            raise StatusError(f"bootstrap lifecycle stage {stage} must remain required")
        if item.get("required_environment") != REQUIRED_ENVIRONMENTS[stage]:
            raise StatusError(f"bootstrap lifecycle stage {stage} has the wrong required environment")
        if item.get("result") != "INSUFFICIENT":
            raise StatusError(f"bootstrap lifecycle stage {stage} cannot carry PASS or FAIL")
        if item.get("relationship") != "missing":
            raise StatusError(f"bootstrap lifecycle stage {stage} must begin with missing evidence")
        if item.get("evidence") != []:
            raise StatusError(f"bootstrap lifecycle stage {stage} cannot contain evidence")

    _forbid_private_fragments(record)


def validate_consumer_pointer(record: Any, repository: str | None = None) -> None:
    """Check only consumer identity and the exact canonical authority pointer.

    Later lifecycle semantics are intentionally left to the canonical shared schema
    and validator. This function must not grow into a second lifecycle validator.
    """

    if not isinstance(record, dict):
        raise StatusError("project status must be an object")
    project = record.get("project")
    if not isinstance(project, str) or not project.strip():
        raise StatusError("project status must contain a non-empty project identity")
    if repository is not None and project != repository:
        raise StatusError(
            f"project status identity {project!r} does not match repository {repository!r}"
        )
    lifecycle = record.get("lifecycle_status")
    if not isinstance(lifecycle, dict) or lifecycle.get("authority") != AUTHORITY:
        raise StatusError("project status does not point to the exact shared Project Status v2 authority")
    _forbid_private_fragments(record)


def write_initial_record(path: Path, repository: str, project_name: str) -> None:
    record = initial_record(repository, project_name)
    validate_initial_bootstrap(record)
    path.write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def load_and_validate_consumer_pointer(path: Path, repository: str | None = None) -> None:
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise StatusError(f"cannot read project status: {exc}") from exc
    validate_consumer_pointer(record, repository)
