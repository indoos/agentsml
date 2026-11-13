# AgentsML

AgentsML is a portable, declarative specification for defining agents, tools, memory, workflows, policies, and protocol-compatible agent systems.

The goal is to describe agent systems once and make them translatable across agent frameworks, runtimes, and interoperability protocols.

## Repository Contents

- `spec/`: draft AgentsML specification chapters.
- `schemas/`: machine-readable JSON Schema for AgentsML documents.
- `examples/`: example AgentsML documents.
- `LICENSE`: MIT license and attribution notice.

The separate workspace-level `../agentsml-ideation/` folder contains research, adapter planning, conformance planning, and spec regeneration material. It is not part of the public spec package itself.

## Current Version

Draft version: `0.2`

The schema accepts `0.1` and `0.2` documents.

What `0.2` adds over `0.1`:

- A normative **condition grammar** for edge conditions: comparisons, boolean operators, parentheses, literals, and `input` / `state` / `steps` references. Expressions outside the grammar must be rejected rather than evaluated.
- Definitions for **fan-out** (one step, two or more unconditional successors) and **joins** (one step, two or more unconditional predecessors), both requiring `agentsml-graph`.
- A **step output** convention: a step whose output is read by a condition produces an object, and free text is stored as `{ "text": ... }`.
- **Approval semantics**: the pause carries a payload, the resumed decision becomes a typed approval result, and a rejected decision must not execute the gated invocation.

Schema:

- [schemas/agentsml.schema.json](schemas/agentsml.schema.json)

Changelog:

- [CHANGELOG.md](CHANGELOG.md)

## Example Documents

- [simple-agent.agentsml.yaml](examples/simple-agent.agentsml.yaml) — Minimal single-agent document.
- [branching-agent.agentsml.yaml](examples/branching-agent.agentsml.yaml) — Draft 0.2: conditional edges, fan-out, and join.
- [credit-risk-agent.agentsml.yaml](examples/credit-risk-agent.agentsml.yaml) — Multi-agent credit risk analysis workflow.
- [fraud-detection-agent.agentsml.yaml](examples/fraud-detection-agent.agentsml.yaml) — Fraud investigation with human-in-the-loop approval.
- [kyc-aml-investigation-agent.agentsml.yaml](examples/kyc-aml-investigation-agent.agentsml.yaml) — KYC/AML investigation pipeline.
- [mcp-integration.agentsml.yaml](examples/mcp-integration.agentsml.yaml) — MCP tool integration.
- [a2a-delegation.agentsml.yaml](examples/a2a-delegation.agentsml.yaml) — A2A protocol agent delegation and card exports.
- [ag-ui-streaming.agentsml.yaml](examples/ag-ui-streaming.agentsml.yaml) — AG-UI streaming and frontend state sync.

## Reference Compiler & CLI

The reference compiler lives in [`agentsml-impl`](../agentsml-impl/) and provides the `agentsml` CLI:

- **`agentsml compile <file> -t <target> -o <dir>`**: Compile an AgentsML document to target-specific agent code.
- **`agentsml graph <file> [--format mermaid|ascii]`**: Render execution graphs as Mermaid flowcharts or ASCII DAGs.
- **`agentsml run <file> -t <target> -q "<query>"`**: Compile and execute against target runtimes.
- **`agentsml validate <file>`**: Schema and semantic validation with diagnostic reports.
- **`agentsml doctor <file> -t <target>`**: Target compatibility analysis and capability reporting.
- **`agentsml list-targets`**: List all 31 compilation targets with wave, level, maturity, and certification.

### Target Support Matrix

The compiler supports 31 targets across 5 waves with 0 scaffolds:

- **11 External-Runtime Certified**: `langgraph`, `google-adk`, `pydantic-ai`, `openai-agents`, `smolagents`, `claude-agent-sdk`, `crewai`, `llamaindex`, `agno`, `mastra`, `vercel-ai`.
- **9 Offline-Behavioral Certified**: `a2a`, `ucp`, `ap2`, `n8n`, `langflow`, `flowise`, `relevance-ai`, `zapier-agents`, `lyzr`.
- **11 Structural Verified**: Cloud platforms (`vertex-agent-engine`, `bedrock-agentcore`, `databricks`, `microsoft-agent-framework`, `snowflake-cortex`, `spring-ai`) and frameworks (`ag2`, `langchain`, `strands-agents`, `mcp-server`, `ag-ui`).

## License

MIT License.

Copyright (c) 2026 Impetus Technologies

Author: Sanjay Sharma
