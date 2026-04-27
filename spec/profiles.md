# AgentsML Profile System Draft

Status: draft v0.1 seed

## Purpose

Profiles let AgentsML stay portable while still describing advanced capabilities.

An AgentsML document may declare required profiles:

```yaml
profiles:
  - agentsml-core
  - agentsml-graph
  - agentsml-mcp
```

Compilers must treat declared profiles as requirements. If a target cannot support a required profile, it must emit a diagnostic.

## Profile Levels

- Required: the document cannot compile correctly without this profile.
- Optional: the document can compile without it, but with reduced capability.
- Target extension: a target-specific profile such as `langgraph.interrupts` or `dify.dsl`.

Suggested syntax:

```yaml
profiles:
  required:
    - agentsml-core
    - agentsml-graph
  optional:
    - agentsml-ui
  extensions:
    - langgraph.checkpoints
```

## Core Profiles

### `agentsml-core`

Includes agents, models, tools, resources, prompts, schemas, simple workflows, state, handoffs, approvals, artifacts, events, and diagnostics.

### `agentsml-graph`

Adds arbitrary edges, cycles, joins, reducers, subgraphs, checkpoint boundaries, interrupt/resume semantics, and graph-level replay.

### `agentsml-conversation`

Adds multi-agent conversation choreography, speaker selection, group chat, debate/critique patterns, and transcript semantics.

### `agentsml-rag`

Adds knowledge bases, indexes, retrievers, document stores, citation policy, provenance, and retrieval evaluation metadata.

### `agentsml-mcp`

Adds MCP servers, tools, resources, prompts, roots, sampling, elicitation, transports, and MCP-specific auth/security bindings.

### `agentsml-a2a`

Adds agent cards, remote skills, tasks, messages, parts, artifacts, streaming status, discovery, and authenticated/extended cards.

### `agentsml-ui`

Adds UI event streams, message deltas, tool-call visibility, state snapshots, state deltas, user input events, and frontend tool execution.

### `agentsml-commerce`

Adds products, carts, checkout, user consent, merchant commitments, fulfillment, cancellation, and refund state.

### `agentsml-payments`

Adds payment mandates, payment authorization, spending limits, signed approval evidence, receipts, and payment audit trails.

### `agentsml-enterprise`

Adds auth, secret references, audit trails, compliance metadata, deployment targets, policy enforcement, and tenant boundaries.

### `agentsml-observability`

Adds trace/span/log/metric mappings, OpenTelemetry alignment, CloudEvents-compatible event envelopes, run replay metadata, and redaction policy.

## Diagnostics

Profile diagnostics should include:

- `unsupported_profile`
- `unsupported_feature`
- `lossy_mapping`
- `requires_adapter`
- `requires_target_extension`
- `missing_policy`
- `missing_auth_binding`
