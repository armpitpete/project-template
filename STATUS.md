---
completion_authority: true
standard: Recursive Project Improvement Standard v1.0
project_slug: project-template
project_name: Project Template
project_type: system
template_mode: true
status: BOOTSTRAP
authority_files:
  - docs/authority/AUTHORITY.md
---

# Project Status

## Current authority

The exact current repository head containing this reusable project-control skeleton.

## Current lane

Maintain and validate the reusable future-project bootstrap.

## Allowed scope

- template control files;
- template initializer;
- project-control validator;
- CI and pull-request control;
- documentation of the bootstrap process.

## Forbidden changes

- project-specific manuscript, product, language, hardware or research content;
- claims that generated repositories are authoritative before initialization;
- weakening singular completion authority;
- bypassing validation.

## Validation

Run:

```bash
python scripts/validate_project_control.py
python scripts/validate_project_control.py --repository armpitpete/project-template
```

Both commands must pass in this repository.

## Done

- Mandatory project-control file set defined.
- Template-mode authority boundary defined.
- Fixed new-chat bootstrap included.
- Deterministic control validator included.
- CI enforcement included.
- Post-template initializer included.

## To do

- Review and promote the exact template implementation.
- Mark the GitHub repository as a template repository.
- Create the central `New-OrderProject.ps1` wrapper.
- Prove one sacrificial repository creation and initialization.

## Next bounded gate

Review and promote the exact project-template implementation, then enable the GitHub template-repository setting.

## Stop point

Stop before creating or promoting a real project from this template until the template implementation is reviewed and its CI passes.
