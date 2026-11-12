# Changelog

All notable changes to the AgentsML draft specification are recorded here.

## Draft 0.2 — 2026-11-12

### Added

- Normative condition grammar for edge conditions: comparisons (`==`, `!=`, `<`, `<=`, `>`, `>=`), boolean operators (`&&`, `||`, `!`), parentheses, literals, and dotted or indexed references rooted at `input`, `state`, or `steps`. Implementations must reject expressions outside the grammar instead of evaluating them as code, and must report a diagnostic for a condition that cannot be parsed.
- Definitions of fan-out (one step with two or more unconditional successors) and joins (one step with two or more unconditional predecessors). Both require the `agentsml-graph` profile.
- Step output convention: a step whose output is read by a condition produces an object; free text is stored as `{ "text": ... }`.
- Approval semantics: the pause carries a payload describing what is being approved, the resumed decision becomes a typed approval result available to later steps, and a rejected decision must not execute the gated invocation.

### Changed

- The JSON Schema now accepts both `0.1` and `0.2` documents. Existing `0.1` documents remain valid.
- The `edge.condition` field in the object model points to the condition grammar.

## Draft 0.1 — initial public spec package

- Six specification chapters: object model, execution semantics, profiles, security and permissions, observability, and diagnostics.
- JSON Schema for AgentsML documents.
- Seven example documents, including MCP, A2A, and AG-UI profiles.
