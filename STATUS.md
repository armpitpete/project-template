---
completion_authority: true
standard: Recursive Project Improvement Standard v1.0
project_slug: project-template
project_name: Project Template
project_type: system
template_mode: true
status: IMPLEMENTING
authority_files:
  - docs/authority/AUTHORITY.md
---

# Project Status

## Current authority

Batch 3 Real-Thing Proof template-consumer candidate is based on exact protected baseline:

`50b15cee57702143161d3d8814ce412cf1124e0e`

Canonical status authorities are version-pinned to:

- Threadkeeper Real-Thing Proof protocol: `a5bc55336c86097301b378d8654ac92a26ef81e5`;
- `armpitpete/merrin-project-controls` Project Status v2: `7bc8b7f5ef921851ad163093f089d28d8128bf6c`.

This repository consumes those controls. It does not redefine them.

## Current lane

Issue #3 / `agent/real-thing-proof-template-v0-1`: make the reusable future-project bootstrap generate an evidence-safe initial Project Status v2 profile and preserve an exact canonical authority pointer without duplicating lifecycle verdict logic.

The lane stops before merge.

## Allowed scope

- template control files and initial repository structure;
- post-template identity initialisation;
- deterministic validation of generated repositories;
- version-pinned adoption of accepted contracts from `merrin-project-controls`;
- deterministic initial `project-status.json` generation for newly initialized repositories;
- bootstrap-profile and canonical-pointer checks that do not reimplement later lifecycle verdicts;
- documentation and tests for the bootstrap path.

## Forbidden changes

- project-specific manuscript, product, language, hardware or research content;
- independent modification or reimplementation of shared-control meaning;
- claims that generated repositories are authoritative before initialisation;
- treating planning percentage, CI, fixtures, or proxy evidence as real lifecycle proof;
- deriving later lifecycle verdicts inside Project Template instead of the canonical shared validator;
- weakening singular completion authority;
- bypassing validation;
- automatic migration of existing repositories;
- deployment, GitHub template-setting mutation, or merge in this lane without its separate protected gate.

## Validation

Run:

```bash
python scripts/validate_project_control.py --repository armpitpete/project-template
cd scripts
python -m unittest -v test_project_status_v2.py
```

CI additionally initializes two disposable temporary copies, validates them, and requires byte-identical privacy-safe `project-status.json` output.

The local bootstrap adapter may self-check only the fixed initial profile and exact canonical pointer. It is not the canonical Project Status v2 lifecycle validator.

## Done

- Mandatory project-control file set defined and merged.
- Template-mode authority boundary defined.
- Fixed new-chat bootstrap included.
- Deterministic control validator and CI enforcement included.
- Post-template initializer included.
- Central local wrapper implemented in Project Folder Checker.
- One disposable repository creation and initialisation proof completed.
- Canonical shared-control authority assigned to `merrin-project-controls`.
- Project Status Engine, Merrin Project Controls, and Project Folder Checker completed earlier Real-Thing Proof rollout batches.

## To do

- complete Batch 3 implementation against exact baseline `50b15cee57702143161d3d8814ce412cf1124e0e`;
- obtain exact-head automated checks;
- obtain independent exact-head review against the canonical schema/validator boundary;
- merge only through a separate protected gate;
- confirm or enable the GitHub template-repository setting only through its own later authority;
- document future upgrade behaviour when a shared contract version changes.

## Next bounded gate

Complete Batch 3 exact-head validation and independent review, then stop before merge.

## Stop point

Do not merge, mutate existing consumers, change the GitHub template setting, deploy, or claim portfolio-wide adoption from this candidate.
