# Changelog

All notable changes to the AgentsML specification are recorded here.

## Specification v0.2 — 2026-11-13

### Added

- **Versioned JSON Schemas**: Formalized versioned schemas under `schemas/v0.1/` (strict v0.1 core schema) and `schemas/v0.2/` (comprehensive v0.2 graph and protocol schema), alongside canonical `schemas/agentsml.schema.json`.
- **Graph Extensions**: Formalized fan-out (concurrent successors), fan-in joins (`join: wait_all` / `join: wait_any`), and cycle semantics under the `agentsml-graph` profile.
- **Normative Condition & Expression Grammar**: Edge conditions and step expressions support `${...}` template expressions with comparisons (`==`, `!=`, `<`, `<=`, `>`, `>=`), boolean operators (`&&`, `||`, `!`), parentheses, literals, and dotted or indexed references (`${steps.<step_id>.output.<field>}`, `${state.<field>[<index>]}`).
- **Protocol Profiles**:
  - `agentsml-mcp`: Formalized `mcp_servers` block with stdio, sse, streamable_http transports and `mcp_tool_name` resolution.
  - `agentsml-a2a`: Formalized `a2a_agents` client bindings and `a2a_server` service exposure configuration.
  - `agentsml-ui`: Formalized AG-UI real-time streaming, SSE event emission, and frontend state synchronization.
- **Public Examples**: All 8 public examples aligned with v0.2 specification and validated with 0 schema or semantic diagnostics.
- **Interactive Documentation & Playground**: Zero-dependency web documentation portal and live interactive compiler playground in `docs/index.html`.

### Changed

- Transitioned specification status from Draft 0.2 to Specification v0.2 across object model, execution semantics, and profile documents.
- Step definitions in JSON Schema explicitly accept `join` and `parallel` execution attributes.

## Draft 0.1 — initial public spec package

- Six specification chapters: object model, execution semantics, profiles, security and permissions, observability, and diagnostics.
- JSON Schema for AgentsML documents.
- Seven example documents, including MCP, A2A, and AG-UI profiles.
