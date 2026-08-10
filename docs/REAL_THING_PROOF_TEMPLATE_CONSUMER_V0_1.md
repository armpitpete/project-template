# Real-Thing Proof template consumer v0.1

## Exact authorities

- Threadkeeper protocol: `armpitpete/threadkeeper@a5bc55336c86097301b378d8654ac92a26ef81e5`.
- Shared Project Status v2: `armpitpete/merrin-project-controls@7bc8b7f5ef921851ad163093f089d28d8128bf6c`.
- Rollout issue: `armpitpete/threadkeeper#123`.
- Local issue: `armpitpete/project-template#3`.
- Exact baseline: `50b15cee57702143161d3d8814ce412cf1124e0e`.

`project-template` consumes these controls. It does not redefine them.

## Generated repository behaviour

A repository created from this template is not authoritative merely because files exist.

After creation, run:

```bash
python scripts/initialise_project.py \
  --repository OWNER/REPOSITORY \
  --project-name "Project name" \
  --project-type TYPE

python scripts/validate_project_control.py \
  --repository OWNER/REPOSITORY
```

Initialisation creates `project-status.json` only in the generated repository. The bootstrap record:

- starts with planning estimate `0`;
- carries all eight lifecycle stages;
- keeps all eight bootstrap lifecycle stages required;
- marks all eight stages `INSUFFICIENT` with missing evidence;
- uses the exact shared Project Status v2 authority pin;
- makes no deployment, live-behaviour, human-acceptance, or completion claim.

The template does not decide that any bootstrap stage is `NOT_APPLICABLE`. A generated project may later change its own required stages only through that project's separate governed authority and the canonical shared lifecycle contract.

## Consumer / validator boundary

`scripts/project_status_v2.py` is intentionally a bootstrap adapter rather than a local copy of the canonical Project Status v2 validator.

It performs two bounded jobs:

1. generate and self-check the fixed initial bootstrap profile;
2. after bootstrap, verify only the repository identity, privacy boundary, and exact `merrin-project-controls@7bc8b7f5ef921851ad163093f089d28d8128bf6c` authority pointer.

It does **not** derive later lifecycle verdicts. Later claims such as `implemented`, `deployed`, `human-acceptance-received`, or `complete` must be evaluated by the canonical shared schema and validator in `merrin-project-controls` under the generated project's own governed lane.

This separation prevents Project Template from becoming a competing shared-control authority.

## Bootstrap evidence boundary

Percentage and likelihood are planning information. They cannot establish lifecycle proof.

Inside the fixed bootstrap profile, no stage may carry PASS/FAIL evidence, proxy substitution, or `NOT_APPLICABLE`; every stage begins required and insufficient. Those are bootstrap-generation invariants, not a replacement lifecycle contract.

## Disposable proof

CI creates two temporary copies of the template, initializes the same generic disposable repository in each, validates both, and compares the generated status records byte-for-byte.

Focused regressions reject bootstrap percentage inflation, proxy/PASS substitution, unsupported completion, lifecycle-stage relaxation, wrong repository identity, and a wrong shared-control authority pointer. A separate regression proves the permanent consumer check does not adjudicate later lifecycle verdicts.

That proves deterministic local bootstrap generation and pointer enforcement only. It does not prove adoption by any existing repository or any real deployment, live behaviour, owner acceptance, or later canonical lifecycle validity.

The disposable copies remain inside the CI runner and are removed when the step exits. No GitHub repository is created or mutated by the proof.

## Migration boundary

Existing repositories and historical status records are unchanged. Adoption by another repository requires its own exact baseline, collision check, issue, branch, validation, review, and protected merge gate.
