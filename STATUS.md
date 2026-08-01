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

`main` at exact commit `820e2ed44484b847a55cf95bfdfc698e6bbf45bd`.

Shared repository-control contracts are governed by `armpitpete/merrin-project-controls` Foundation v0.1 at exact commit `b784573ad86d8d54ba1108dc1bf952260ee4c6bb`.

## Current lane

Maintain the reusable future-project bootstrap as a version-pinned consumer of the canonical shared-control contracts.

The template may package approved controls, but it must not redefine them or become a competing authority.

## Allowed scope

- template control files and initial repository structure;
- post-template identity initialisation;
- deterministic validation of generated repositories;
- version-pinned adoption of accepted contracts from `merrin-project-controls`;
- documentation and tests for the bootstrap path.

## Forbidden changes

- project-specific manuscript, product, language, hardware or research content;
- independent modification of shared-control meaning;
- claims that generated repositories are authoritative before initialisation;
- weakening singular completion authority;
- bypassing validation;
- automatic migration of existing repositories.

## Validation

Run:

```bash
python scripts/validate_project_control.py
python scripts/validate_project_control.py --repository armpitpete/project-template
```

Both commands must pass in this repository.

## Done

- Mandatory project-control file set defined and merged.
- Template-mode authority boundary defined.
- Fixed new-chat bootstrap included.
- Deterministic control validator and CI enforcement included.
- Post-template initializer included.
- Central local wrapper implemented in Project Folder Checker.
- One disposable repository creation and initialisation proof completed.
- Canonical shared-control authority assigned to `merrin-project-controls`.

## To do

- replace copied control meaning with explicit version references to `merrin-project-controls`;
- prove one bounded Foundation v0.1 consumer integration;
- confirm or enable the GitHub template-repository setting;
- document upgrade behaviour when a shared contract version changes.

## Next bounded gate

Adopt one Foundation v0.1 contract by exact version and prove that a newly generated disposable fixture validates without duplicating or weakening the canonical contract.

## Stop point

Stop before bulk adoption, existing-repository migration or any shared-contract change outside `merrin-project-controls`.
