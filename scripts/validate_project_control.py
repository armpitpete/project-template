#!/usr/bin/env python3
"""Validate mandatory repository project-control structure."""

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

from project_status_v2 import AUTHORITY as PROJECT_STATUS_AUTHORITY
from project_status_v2 import StatusError, load_and_validate

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_REPOSITORY = "armpitpete/project-template"
THREADKEEPER_AUTHORITY = "a5bc55336c86097301b378d8654ac92a26ef81e5"
SHARED_CONTROL_AUTHORITY = "7bc8b7f5ef921851ad163093f089d28d8128bf6c"
VALID_STATUSES = {
    "UNASSESSED",
    "DIAGNOSTIC",
    "DESIGN",
    "AUTHORISED",
    "IMPLEMENTING",
    "VALIDATING",
    "REVIEW",
    "READY",
    "AUTHORITATIVE",
    "BLOCKED",
    "SUPERSEDED",
    "CLOSED",
    "BOOTSTRAP",
}
REQUIRED_FILES = [
    "AGENTS.md",
    "STATUS.md",
    "docs/authority/AUTHORITY.md",
    "scripts/validate_project_control.py",
    "scripts/initialise_project.py",
    "scripts/project_status_v2.py",
    ".github/REPOSITORY_WRITE_RULES.md",
    ".github/workflows/project-control.yml",
    ".github/pull_request_template.md",
]
REQUIRED_STATUS_HEADINGS = [
    "Current authority",
    "Current lane",
    "Allowed scope",
    "Forbidden changes",
    "Validation",
    "Done",
    "To do",
    "Next bounded gate",
    "Stop point",
]
REQUIRED_AUTHORITY_HEADINGS = [
    "Source authority",
    "Active authority",
    "Decision authority",
    "Completion authority",
    "Governing constraints",
]
FORBIDDEN_TOKENS = [
    "TODO_" + "REPLACE",
    "REPLACE_" + "ME",
    "[" + "PROJECT_NAME" + "]",
    "[" + "REPOSITORY" + "]",
    "<" + "PROJECT_NAME" + ">",
    "<" + "REPOSITORY" + ">",
]


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repository",
        default=os.environ.get("GITHUB_REPOSITORY", ""),
        help="OWNER/REPOSITORY; defaults to GITHUB_REPOSITORY",
    )
    return parser.parse_args()


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def front_matter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        raise ValueError("missing YAML front matter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("unterminated YAML front matter")
    data: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line or line.startswith(" ") or line.lstrip().startswith("-"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def markdown_files() -> list[Path]:
    ignored = {".git", ".venv", "node_modules", "vendor"}
    return [
        path
        for path in ROOT.rglob("*.md")
        if not any(part in ignored for part in path.parts)
    ]


def main() -> int:
    args = arguments()
    failures: list[str] = []

    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            failures.append(f"missing required file: {relative}")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    status_text = read("STATUS.md")
    agents_text = read("AGENTS.md")
    authority_text = read("docs/authority/AUTHORITY.md")
    rules_text = read(".github/REPOSITORY_WRITE_RULES.md")

    if THREADKEEPER_AUTHORITY not in rules_text:
        failures.append("repository write rules must pin the canonical Threadkeeper protocol")
    if SHARED_CONTROL_AUTHORITY not in rules_text:
        failures.append("repository write rules must pin the shared Project Status v2 control")
    if PROJECT_STATUS_AUTHORITY != (
        "armpitpete/merrin-project-controls@" + SHARED_CONTROL_AUTHORITY
    ):
        failures.append("local Project Status v2 helper authority does not match the pinned shared control")

    try:
        status_meta = front_matter(status_text)
    except ValueError as exc:
        failures.append(f"STATUS.md {exc}")
        status_meta = {}

    if status_meta.get("completion_authority") != "true":
        failures.append("STATUS.md must declare completion_authority: true")

    if status_meta.get("standard") != "Recursive Project Improvement Standard v1.0":
        failures.append("STATUS.md must name Recursive Project Improvement Standard v1.0")

    status = status_meta.get("status", "")
    if status not in VALID_STATUSES:
        failures.append(f"invalid or missing status: {status!r}")

    template_mode = status_meta.get("template_mode", "")
    if template_mode not in {"true", "false"}:
        failures.append("template_mode must be true or false")

    repository = args.repository.strip()
    if template_mode == "true":
        if repository and repository != TEMPLATE_REPOSITORY:
            failures.append(
                f"template_mode: true is allowed only for {TEMPLATE_REPOSITORY}, "
                f"not {repository}"
            )
        if status_meta.get("project_slug") != "project-template":
            failures.append("template repository project_slug must be project-template")
        if (ROOT / "project-status.json").exists():
            failures.append(
                "template repository must not contain a project-status.json fixture; "
                "the initializer creates it only in generated repositories"
            )
    else:
        if not repository:
            failures.append(
                "non-template validation requires --repository or GITHUB_REPOSITORY"
            )
        if status_meta.get("project_slug") in {"", "project-template"}:
            failures.append("generated repository identity has not been initialized")
        project_status_path = ROOT / "project-status.json"
        if not project_status_path.is_file():
            failures.append("generated repository is missing project-status.json")
        else:
            try:
                load_and_validate(project_status_path)
            except StatusError as exc:
                failures.append(f"project-status.json {exc}")

    for heading in REQUIRED_STATUS_HEADINGS:
        count = len(re.findall(rf"(?m)^## {re.escape(heading)}\s*$", status_text))
        if count != 1:
            failures.append(
                f"STATUS.md must contain exactly one '## {heading}' heading; found {count}"
            )

    for heading in REQUIRED_AUTHORITY_HEADINGS:
        count = len(re.findall(rf"(?m)^## {re.escape(heading)}\s*$", authority_text))
        if count != 1:
            failures.append(
                "docs/authority/AUTHORITY.md must contain exactly one "
                f"'## {heading}' heading; found {count}"
            )

    if "entry_authority: true" not in agents_text:
        failures.append("AGENTS.md must declare entry_authority: true")
    if "Fixed new-chat bootstrap" not in agents_text:
        failures.append("AGENTS.md must include the fixed new-chat bootstrap")
    if "Recursive Project Improvement Standard v1.0" not in agents_text:
        failures.append("AGENTS.md must name the parent standard")

    completion_claims: list[str] = []
    for path in markdown_files():
        text = path.read_text(encoding="utf-8")
        try:
            metadata = front_matter(text)
        except ValueError:
            metadata = {}
        if metadata.get("completion_authority") == "true":
            completion_claims.append(path.relative_to(ROOT).as_posix())

    if completion_claims != ["STATUS.md"]:
        failures.append(
            "exactly root STATUS.md must claim completion authority; found "
            + ", ".join(completion_claims)
        )

    for relative in REQUIRED_FILES:
        text = read(relative)
        for token in FORBIDDEN_TOKENS:
            if token in text:
                failures.append(f"{relative} contains unresolved token {token!r}")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        print(f"Project control failed with {len(failures)} error(s).")
        return 1

    print("PASS: mandatory project-control structure is valid")
    print(f"repository={repository or '(not supplied; template-local mode)'}")
    print(f"status={status}")
    print(f"template_mode={template_mode}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
