# Contributing to the AgentsML specification

This repo holds the public AgentsML specification: prose chapters in `spec/`,
JSON Schemas in `schemas/`, validated examples in `examples/`, and the
release notes in `CHANGELOG.md`. The compiler, language server and playground
live in sibling repos (see the [workspace README](../README.md) if you have
the workspace layout; otherwise see each repo's README).

## Layout

| Path | What it is | Generated? |
|---|---|---|
| `spec/*.md` | Specification chapters | No |
| `schemas/agentsml.schema.json` | Canonical JSON Schema (Draft 2020-12). Accepts `agentsml: "0.1"`, `"0.2"`, `"0.3"`, `"0.4"`. | No |
| `schemas/vX.Y/agentsml.schema.json` | Versioned schema for one spec version | Copied from canonical, then edited |
| `examples/*.agentsml.yaml` | Validated example documents (CI requires at least 9) | No |
| `docs/index.html` | Interactive docs and playground | **Yes**, by `agentsml-ideation/scripts/build_docs_site.py` |
| `CHANGELOG.md` | Spec release notes | No |

Do not hand-edit `docs/index.html`. Regenerating it needs the `agentsml-ideation`
repo and `agentsml-impl`; see "After the spec change" below.

## Checking your change

CI (`.github/workflows/ci.yml`) runs on pushes and pull requests to `main`. It
checks that every schema is valid Draft 2020-12 and that each example validates
against the schema for its declared `agentsml` version. For the examples it uses
`schemas/v<version>/` when it exists, and the canonical schema otherwise. It
also checks that `docs/schemas/` (the copies served on GitHub Pages at each
schema's `$id`) matches `schemas/`: after any schema change run
`python3 scripts/publish_schemas.py` and commit the result.

To run the same checks locally:

```bash
python3 -m pip install jsonschema pyyaml
# then run the two python -c blocks from .github/workflows/ci.yml
python3 scripts/publish_schemas.py --check
```

The compiler also validates examples against the schema and semantic rules:

```bash
cd ../agentsml-impl
uv run --frozen agentsml validate ../agentsml/examples/*.agentsml.yaml
```

## Proposing a spec change

1. **Open an issue first** with the `spec_change` template. Describe the problem,
   the proposed semantics, and which profiles and targets it affects.
2. **Branch from `main`.** Make one logical change per branch.
3. **Prose.** Edit the chapter in `spec/` (`object-model.md`, `execution-semantics.md`,
   `profiles.md`, `diagnostics.md`, `security-permissions.md`, `observability.md`).
   If you add a chapter, list it in `spec/README.md`. If you add a diagnostic code,
   document it in `spec/diagnostics.md`.
4. **Schema.** Edit `schemas/agentsml.schema.json` first. For a new spec version,
   copy it to `schemas/vX.Y/agentsml.schema.json` and set `$id` to the versioned URL.
   Do not copy blindly. The released versioned schemas already differ from the
   canonical one (`$id`, and a stricter `additionalProperties` in v0.3), so review
   the diff with `diff` before you commit.
5. **Example.** Add or update a file in `examples/`. Set `agentsml:` to the version
   it targets. Examples are the living test of the spec, so add one for new fields
   where the existing examples do not show them.
6. **Changelog.** Add an entry at the top of `CHANGELOG.md`, in the existing style
   (`## X.Y.Z — YYYY-MM-DD`, a `Specification version:` line, then `### Added` /
   `### Changed` / `### Fixed`). State whether the change is additive. Documents for
   earlier versions must keep validating, or the changelog must call out the break.
7. **Run the checks** above, then open a pull request with `.github/pull_request_template.md`.

## After the spec change (maintainers)

These repos hold copies or generated output of the schema and examples:

- **Language server:** `cd ../agentsml-ide/language-server && python3 scripts/sync_schema.py`.
  The IDE CI fails if the bundled copy differs (`--check`).
- **Compiler:** copy the canonical and versioned schemas into
  `../agentsml-impl/src/agentsml_impl/schemas/`. Check each file with `cmp`.
  Update targets for any semantic change (see `agentsml-impl/docs/adding-a-target.md`).
- **Playground:** `cd ../agentsml-impl && uv run --frozen python ../agentsml-ideation/scripts/build_docs_site.py`
  regenerates `docs/index.html`.
- **Milestone:** record the change in `agentsml-ideation/TASKS.md`.

## Commits and releases

- Commit subjects use a short prefix: `spec:`, `feat(spec):`, `docs(spec):`, `ci:`,
  `release:`. Use the imperative mood.
- Spec releases cut the `CHANGELOG.md` heading, remove any "draft" wording, and tag the
  release (`v0.3.0` for the current version). Tags are created by maintainers.
