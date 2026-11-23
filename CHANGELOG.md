# Changelog

All notable changes to the AgentsML specification are recorded here.

## 0.4.0 — 2026-11-23

Specification version: `0.4.0`

Additive and backward compatible; v0.3 documents validate unchanged. Schema: `schemas/v0.4/agentsml.schema.json`; the canonical schema also accepts `agentsml: "0.4"`. The reference compiler (`agentsml-impl` 0.4.0) maps all three fields on its 15 code targets; other targets emit `lossy_mapping` where they cannot honour them.

### Added

- Agent `limits` object with `max_turns` (integer >= 1). Exceeding it fails the invocation with error kind `limit_exceeded`, which is not retried; step `fallback` applies.
- Agent `handoffs`: array of agent keys or `{agent, description}` objects. The receiving agent continues the same conversation and its output becomes the step output. Referenced agents must be defined and may not be the agent itself.
- Tool `isolation` (`thread` default, `process`): `process` runs the tool body in a separate OS process that is terminated when `timeout` expires.
- Spec sections: object-model "Additions in v0.4", execution-semantics "Limits, handoffs and tool isolation (v0.4)".
- Example `examples/handoff-agent.agentsml.yaml`.

## 0.3.1 — 2026-11-18

Specification version: `0.3.1` (clarifications; no schema content change).

### Changed

- JSON Schema `$id` values now use the published GitHub Pages URLs under `https://indoos.github.io/agentsml/schemas/` (canonical: `.../schemas/agentsml.schema.json`; versioned: `.../schemas/v0.1/`, `v0.2/`, `v0.3/` `agentsml.schema.json`). The previous `https://agentsml.org/...` identifiers did not resolve. Schema content is otherwise unchanged; all `$ref`s are fragment-only and unaffected.
- Schemas are published to `docs/schemas/` by `scripts/publish_schemas.py` (`--check` runs in CI), and the Pages deploy workflow now also triggers on `schemas/**`. Version index: `docs/schemas/index.html`.
- Execution semantics: tool `timeout` bounds the tool body only (approval wait excluded); on expiry the model receives `tool <name> timed out after <n>s` and the run continues.

## 0.3.0 — 2026-11-17

Specification version: `0.3.0`

Additive and backward compatible; v0.2 documents validate unchanged. Schema: `schemas/v0.3/agentsml.schema.json`; the canonical schema also accepts `agentsml: "0.3"`.

### Added

- Execution semantics: tool approval and step retry/timeout/fallback mappings for the 15 targets that declare them.

- Typed step `retry` object (`max_attempts`, `backoff`, `initial_interval`, `max_interval`, `on_timeout`) and object form of step `approval`.
- Step `fallback` object (`output`, `model`) giving `retry.on_timeout: fallback` a value or fallback model; `fallback.model` must reference a declared model.
- Agent `reasoning` object (`effort`, `budget_tokens`, `expose_trace`).
- Tool `needs_approval` and `approval_mode` (`always`, `once_per_session`, `per_arguments`).
- Spec sections: object-model "Additions in v0.3", execution-semantics "Retry and timeout semantics (v0.3)".
- Example `examples/resilient-agent.agentsml.yaml`.
- Target support (per each target's `capabilities.yaml` in agentsml-impl; 15 of the 31 targets declare these features, the rest, including spring-ai and the cloud and export targets, do not and emit `lossy_mapping`):
  - Tool approval: native in LangGraph, LangChain, OpenAI Agents, Google ADK, Agno; adapter in AG2, Claude Agent SDK, CrewAI, LlamaIndex, Mastra, Microsoft Agent Framework, PydanticAI, smolagents, Strands Agents, Vercel AI SDK.
  - Step retry: native in LangGraph and Mastra; adapter in the other 13.
  - `on_timeout` (timeout and fallback): native in LangGraph; adapter in the other 14.
  - Agent reasoning: native in AG2, Agno, Claude Agent SDK, Google ADK, LangChain, LlamaIndex, Microsoft Agent Framework, OpenAI Agents, PydanticAI, Strands Agents; adapter in CrewAI, LangGraph, Mastra, smolagents, Vercel AI SDK.

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
