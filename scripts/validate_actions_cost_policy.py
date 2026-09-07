#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

HOSTED = re.compile(r"\b(?:ubuntu|windows|macos)-(?:latest|[0-9][A-Za-z0-9._-]*)\b", re.I)
RUNS_ON_LINE = re.compile(r"^(?P<indent>[ \t]*)runs-on:[ \t]*(?P<value>[^\r\n]*)$", re.I)
UPLOAD_ARTIFACT = re.compile(r"uses:\s*actions/upload-artifact@", re.I)
UPLOAD_PAGES_ARTIFACT = re.compile(r"uses:\s*actions/upload-pages-artifact@", re.I)
CACHE_ACTION = re.compile(r"uses:\s*actions/cache@", re.I)
SETUP_CACHE = re.compile(r"(?m)^\s*cache:\s*(?:pip|npm|yarn|pnpm|gradle|maven)\s*$", re.I)


def runs_on_selectors(text: str) -> list[str]:
    lines = text.splitlines()
    selectors: list[str] = []
    for index, line in enumerate(lines):
        match = RUNS_ON_LINE.match(line)
        if not match:
            continue
        inline = match.group("value").strip()
        if inline:
            selectors.append(inline)
            continue

        base_indent = len(match.group("indent"))
        block: list[str] = []
        for following in lines[index + 1 :]:
            if not following.strip():
                if block:
                    break
                continue
            indent = len(following) - len(following.lstrip(" \t"))
            if indent <= base_indent:
                break
            block.append(following.strip())
        selectors.append(" ".join(block) if block else "<empty-runs-on>")
    return selectors


def fail(failures: list[dict[str, str]], rel: str, rule: str, detail: str) -> None:
    failures.append({"file": rel, "rule": rule, "detail": detail})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--private", action="store_true")
    parser.add_argument("--repository-label", required=True)
    args = parser.parse_args()

    root = Path(args.root)
    workflows = sorted((root / ".github" / "workflows").glob("*.y*ml"))
    failures: list[dict[str, str]] = []

    for path in workflows:
        text = path.read_text(encoding="utf-8")
        rel = str(path.relative_to(root))

        if not args.private:
            continue

        for match in HOSTED.finditer(text):
            fail(failures, rel, "private-hosted-runner-forbidden", match.group(0))

        if CACHE_ACTION.search(text) or SETUP_CACHE.search(text):
            fail(
                failures,
                rel,
                "github-actions-cache-forbidden",
                "use runner-local cache instead",
            )

        if UPLOAD_ARTIFACT.search(text):
            fail(
                failures,
                rel,
                "github-actions-artifact-storage-forbidden",
                "write evidence to owned storage instead of actions/upload-artifact",
            )

        if UPLOAD_PAGES_ARTIFACT.search(text):
            fail(
                failures,
                rel,
                "github-pages-artifact-storage-forbidden",
                "private repositories must not use GitHub-hosted artifact storage",
            )

        for selector in runs_on_selectors(text):
            lower = selector.lower()
            if "self-hosted" not in lower:
                fail(
                    failures,
                    rel,
                    "private-runner-must-be-owned-self-hosted",
                    selector,
                )
                continue

            if args.repository_label.lower() not in lower:
                fail(
                    failures,
                    rel,
                    "self-hosted-selector-missing-repository-label",
                    f"{selector} (missing {args.repository_label})",
                )

            if "linux" in lower:
                required = ("arm64", "oracle-ci")
                missing = [token for token in required if token not in lower]
                if missing:
                    fail(
                        failures,
                        rel,
                        "self-hosted-linux-selector-incomplete",
                        f"{selector} (missing {','.join(missing)})",
                    )

    result = {
        "policy_version": 2,
        "private": bool(args.private),
        "repository_label": args.repository_label,
        "workflows_scanned": len(workflows),
        "failures": failures,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 2 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
