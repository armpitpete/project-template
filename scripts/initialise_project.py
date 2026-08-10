#!/usr/bin/env python3
"""Initialize a repository created from armpitpete/project-template."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from project_status_v2 import write_initial_record

ROOT = Path(__file__).resolve().parents[1]
STATUS_PATH = ROOT / "STATUS.md"
AUTHORITY_PATH = ROOT / "docs" / "authority" / "AUTHORITY.md"
PROJECT_STATUS_PATH = ROOT / "project-status.json"

VALID_TYPES = {"story", "language", "product", "hardware", "research", "system", "other"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", required=True, help="OWNER/REPOSITORY")
    parser.add_argument("--project-name", required=True)
    parser.add_argument("--project-type", required=True, choices=sorted(VALID_TYPES))
    return parser.parse_args()


def repository_slug(repository: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise SystemExit("--repository must use OWNER/REPOSITORY")
    return repository.split("/", 1)[1]


def replace_front_matter_value(text: str, key: str, value: str) -> str:
    pattern = rf"(?m)^{re.escape(key)}:\s*.*$"
    replacement = f"{key}: {value}"
    updated, count = re.subn(pattern, replacement, text, count=1)
    if count != 1:
        raise SystemExit(f"Missing or repeated front-matter key: {key}")
    return updated


def main() -> int:
    args = parse_args()
    slug = repository_slug(args.repository)

    if args.repository == "armpitpete/project-template":
        raise SystemExit("Refusing to initialize the template repository as a generated project.")

    status = STATUS_PATH.read_text(encoding="utf-8")
    status = replace_front_matter_value(status, "project_slug", slug)
    status = replace_front_matter_value(status, "project_name", args.project_name)
    status = replace_front_matter_value(status, "project_type", args.project_type)
    status = replace_front_matter_value(status, "template_mode", "false")

    status = re.sub(
        r"## Current authority\n.*?\n## Current lane",
        "## Current authority\n\nInitial generated repository authority pending bounded source assessment.\n\n"
        "## Current lane",
        status,
        count=1,
        flags=re.DOTALL,
    )
    status = re.sub(
        r"## Current lane\n.*?\n## Allowed scope",
        "## Current lane\n\nRepository bootstrap and source assessment.\n\n## Allowed scope",
        status,
        count=1,
        flags=re.DOTALL,
    )
    status = re.sub(
        r"## Done\n.*?\n## To do",
        "## Done\n\n"
        "- Repository created from the mandatory project template.\n"
        "- Repository identity initialized.\n"
        "- Project-control validator installed.\n"
        "- Initial Project Status v2 record generated with no unsupported lifecycle PASS.\n\n"
        "## To do",
        status,
        count=1,
        flags=re.DOTALL,
    )
    status = re.sub(
        r"## To do\n.*?\n## Next bounded gate",
        "## To do\n\n"
        "- Identify and preserve source material.\n"
        "- Establish exact project authority.\n"
        "- Classify the first bounded implementation lane.\n"
        "- Replace missing lifecycle evidence only with direct evidence from the required real environment.\n\n"
        "## Next bounded gate",
        status,
        count=1,
        flags=re.DOTALL,
    )
    status = re.sub(
        r"## Next bounded gate\n.*?\n## Stop point",
        "## Next bounded gate\n\n"
        "Assess and inventory project sources without modifying them.\n\n"
        "## Stop point",
        status,
        count=1,
        flags=re.DOTALL,
    )
    status = re.sub(
        r"## Stop point\n.*\Z",
        "## Stop point\n\n"
        "Stop before implementation, editing or promotion until source authority is established.\n",
        status,
        count=1,
        flags=re.DOTALL,
    )

    STATUS_PATH.write_text(status, encoding="utf-8", newline="\n")

    authority = AUTHORITY_PATH.read_text(encoding="utf-8")
    authority += (
        f"\n## Generated repository identity\n\n"
        f"- Repository: `{args.repository}`\n"
        f"- Project: {args.project_name}\n"
        f"- Type: `{args.project_type}`\n"
        f"- Initialization state: identity established; source authority pending assessment.\n"
    )
    AUTHORITY_PATH.write_text(authority, encoding="utf-8", newline="\n")

    write_initial_record(PROJECT_STATUS_PATH, args.repository, args.project_name)

    print(f"Initialized {args.repository}")
    print("Generated project-status.json with lifecycle_status.verified=insufficient")
    print(
        "Next: python scripts/validate_project_control.py "
        f"--repository {args.repository}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
