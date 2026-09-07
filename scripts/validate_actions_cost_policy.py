#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

HOSTED = re.compile(r"\b(?:ubuntu|windows|macos)-(?:latest|[0-9][A-Za-z0-9._-]*)\b", re.I)
RUNS_ON = re.compile(r"(?m)^\s*runs-on:\s*(.+?)\s*$")
UPLOAD = re.compile(r"uses:\s*actions/upload-artifact@", re.I)
CACHE_ACTION = re.compile(r"uses:\s*actions/cache@", re.I)
SETUP_CACHE = re.compile(r"(?m)^\s*cache:\s*(?:pip|npm|yarn|pnpm|gradle|maven)\s*$", re.I)
RETENTION = re.compile(r"(?m)^\s*retention-days:\s*(\d+)\s*$")

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", default=".")
    p.add_argument("--private", action="store_true")
    p.add_argument("--repository-label", required=True)
    p.add_argument("--max-artifact-retention-days", type=int, default=1)
    args = p.parse_args()

    root = Path(args.root)
    workflows = sorted((root / ".github" / "workflows").glob("*.y*ml"))
    failures: list[dict[str, str]] = []

    for path in workflows:
        text = path.read_text(encoding="utf-8")
        rel = str(path.relative_to(root))

        if args.private:
            for m in HOSTED.finditer(text):
                failures.append({"file": rel, "rule": "private-hosted-runner-forbidden", "detail": m.group(0)})

            if CACHE_ACTION.search(text) or SETUP_CACHE.search(text):
                failures.append({"file": rel, "rule": "github-actions-cache-forbidden", "detail": "use runner-local cache instead"})

            # All explicit self-hosted Linux selectors must carry the hardened Oracle routing identity.
            for line in RUNS_ON.findall(text):
                if "self-hosted" in line and "Linux" in line:
                    required = ("ARM64", "oracle-ci", args.repository_label)
                    missing = [token for token in required if token not in line]
                    if missing:
                        failures.append({
                            "file": rel,
                            "rule": "self-hosted-linux-selector-incomplete",
                            "detail": "missing " + ",".join(missing),
                        })

            if UPLOAD.search(text):
                retentions = [int(v) for v in RETENTION.findall(text)]
                if not retentions:
                    failures.append({"file": rel, "rule": "artifact-retention-missing", "detail": "upload-artifact requires explicit short retention"})
                elif max(retentions) > args.max_artifact_retention_days:
                    failures.append({
                        "file": rel,
                        "rule": "artifact-retention-too-long",
                        "detail": f"max={max(retentions)} allowed={args.max_artifact_retention_days}",
                    })

    result = {
        "policy_version": 1,
        "private": bool(args.private),
        "repository_label": args.repository_label,
        "workflows_scanned": len(workflows),
        "failures": failures,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 2 if failures else 0

if __name__ == "__main__":
    raise SystemExit(main())
