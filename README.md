# Project Template

Mandatory bootstrap template for new projects in the `armpitpete` repository estate.

## Purpose

A project is not ready for substantive work until its project-control validator passes.

Every repository created from this template begins with:

- `AGENTS.md` — mandatory entry and session rules;
- `STATUS.md` — sole repository-level completion authority;
- `docs/authority/AUTHORITY.md` — authority model;
- `scripts/validate_project_control.py` — deterministic control validator;
- `.github/workflows/project-control.yml` — CI enforcement;
- `.github/pull_request_template.md` — exact-scope review prompts.

## Template state

This repository deliberately uses:

```yaml
template_mode: true
status: BOOTSTRAP
```

Generated repositories must run the initializer before substantive work:

```bash
python scripts/initialise_project.py \
  --repository OWNER/REPOSITORY \
  --project-name "Human Project Name" \
  --project-type "story|language|product|hardware|research|other"
```

The initializer changes `template_mode` to `false`, writes the new repository identity,
and leaves the project in a controlled `BOOTSTRAP` lane for source assessment.

## Required first lane

```text
Repository creation
→ initializer
→ project-control validation
→ source assessment
→ authority declaration
→ first bounded implementation contract
```

Do not add the repository to `ACTIVE_WORK.md` until actual project work begins.

## Parent standard

`Recursive Project Improvement Standard v1.0`
