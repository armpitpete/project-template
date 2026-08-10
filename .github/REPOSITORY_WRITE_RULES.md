# Repository Write Rules — Real-Thing Proof template consumer v0.1

## Canonical authorities

This repository consumes, but does not redefine, these exact authorities:

```text
Threadkeeper protocol:
  repository: armpitpete/threadkeeper
  commit: a5bc55336c86097301b378d8654ac92a26ef81e5
  protocol: docs/REAL_THING_PROOF_AND_COMPLETION_STATUS_V0_1.md

Shared Project Status v2 control:
  repository: armpitpete/merrin-project-controls
  commit: 7bc8b7f5ef921851ad163093f089d28d8128bf6c
  schema: schemas/project-status.schema.json
  validator: scripts/validate_project_status.py
```

Local template controls may strengthen the initial bootstrap state. They must not weaken, fork, reimplement, or compete with the canonical lifecycle contract.

## Governing rule

> Never test a proxy when the claim concerns the real thing. Never allow `complete` to absorb implementation, deployment, live verification and human acceptance into one vague word.

## Template boundary

`project-template` is a reusable bootstrap consumer. It is not the shared-contract authority.

A generated repository receives a deterministic initial `project-status.json` only when `scripts/initialise_project.py` is run for that repository. The template repository itself must not carry a fake project-status fixture.

The generated bootstrap record must:

- preserve all eight lifecycle stages separately;
- keep all eight bootstrap lifecycle stages required;
- start all eight stages without unsupported PASS evidence;
- keep planning percentage and completion likelihood separate from lifecycle proof;
- point to the exact shared Project Status v2 authority;
- contain no credential, private inventory, local-path, or control-plane material.

The template cannot decide that a bootstrap stage is `NOT_APPLICABLE`. Any later project-specific relaxation belongs to the generated project's own governed authority and must be evaluated under the canonical shared schema and validator.

## Validator boundary

`scripts/project_status_v2.py` is a bootstrap adapter, not a second Project Status v2 implementation.

It may:

- generate the fixed initial bootstrap profile;
- reject inflation or relaxation inside that initial profile;
- verify that a later record still names the correct repository and exact canonical shared-control authority.

It must not:

- derive or verify later lifecycle statuses;
- reproduce the canonical lifecycle verdict algorithm;
- decide whether later evidence is sufficient for `implemented`, `deployed`, `complete`, or any other lifecycle claim;
- replace `merrin-project-controls/scripts/validate_project_status.py`.

Later lifecycle semantics must be checked by the exact canonical shared control under the generated project's own governed lane.

## Fixture boundary

A disposable generated fixture may prove:

- deterministic template generation;
- local bootstrap-profile behaviour;
- the version pin used by the generated status record;
- rejection of bootstrap percentage inflation and proxy substitution;
- rejection of template-level lifecycle relaxation;
- privacy-safe generic output.

It does not prove a real consumer has deployed, behaves correctly live, received human acceptance, or passed the canonical lifecycle validator after later project changes.

## Existing-repository boundary

This lane does not migrate or rewrite existing repositories. Each existing consumer needs its own collision-checked issue, exact branch, validation, review, and merge authority.

## Protected boundaries

This lane does not authorise:

- shared-control redefinition;
- existing-repository migration;
- lifecycle reclassification;
- deployment or production activation;
- GitHub template-repository setting changes;
- historical record rewriting;
- disclosure of private repository inventory or credentials;
- merge without exact-head checks and independent review;
- a portfolio-wide adoption or completion claim.

## Adoption record

- rollout issue: `armpitpete/threadkeeper#123`;
- local issue: `armpitpete/project-template#3`;
- baseline: `50b15cee57702143161d3d8814ce412cf1124e0e`;
- branch: `agent/real-thing-proof-template-v0-1`;
- canonical Threadkeeper release: `a5bc55336c86097301b378d8654ac92a26ef81e5`;
- shared Project Status v2 authority: `7bc8b7f5ef921851ad163093f089d28d8128bf6c`.
