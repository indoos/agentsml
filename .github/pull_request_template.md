## What and why

<!-- One or two sentences. Link the spec_change issue. -->

## Spec checklist

- [ ] Prose updated in `spec/` (and `spec/README.md` if a chapter was added)
- [ ] `schemas/agentsml.schema.json` updated first; versioned copy `schemas/vX.Y/` created or updated, with `$id` set and the diff reviewed
- [ ] At least one example in `examples/` shows the change, and its `agentsml:` version is set
- [ ] `CHANGELOG.md` entry added, and it says whether the change is additive
- [ ] The schema CI checks pass locally (see CONTRIBUTING.md)

## Follow-ups (maintainers)

- [ ] `agentsml-ide/language-server/scripts/sync_schema.py` run
- [ ] Compiler schema copies updated and checked with `cmp`
- [ ] Playground `docs/index.html` regenerated
- [ ] Milestone entry in `agentsml-ideation/TASKS.md`
