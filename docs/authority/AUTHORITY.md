---
authority_record: true
standard: Recursive Project Improvement Standard v1.0
---

# Project Authority

## Source authority

For the template repository:

- the exact promoted `main` commit;
- preserved repository history;
- `Recursive Project Improvement Standard v1.0`.

For a generated repository:

- the generated template commit;
- source material identified during the first bounded assessment lane;
- preserved imports and manifests created by that lane.

## Active authority

`STATUS.md` is the sole repository-level completion authority.

The active editable source must be declared during source assessment before substantive work begins.

## Decision authority

Substantial changes require a bounded contract recording:

- one observable goal;
- exact starting authority;
- allowed changes;
- forbidden changes;
- expected result;
- validation;
- promotion rule;
- stop rule.

## Completion authority

Exactly one Markdown file may declare:

```yaml
completion_authority: true
```

That file must be root `STATUS.md`.

## Governing constraints

- `template_mode: true` is permitted only in `armpitpete/project-template`.
- A generated repository must be initialized before project work begins.
- No unresolved repository identity may pass validation.
- No competing status document may claim current completion authority.
- Repository evidence outranks chat memory.
- No new lane begins automatically after closure of the current lane.
