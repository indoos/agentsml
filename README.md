# AgentsML

AgentsML is a portable, declarative specification for defining agents, tools, memory, workflows, policies, and protocol-compatible agent systems.

The goal is to describe agent systems once and make them translatable across agent frameworks, runtimes, and interoperability protocols.

## Repository Contents

- `docs/`: [Interactive Documentation & Web Playground](docs/index.html) — live visual graph renderer, target code generator, and specification explorer.
- `spec/`: AgentsML specification chapters (object model, execution semantics, profiles, diagnostics, security, observability).
- `schemas/`: Machine-readable JSON Schemas ([v0.2](schemas/v0.2/agentsml.schema.json), [v0.1](schemas/v0.1/agentsml.schema.json), and canonical [agentsml.schema.json](schemas/agentsml.schema.json)).
- `examples/`: Validated example AgentsML documents (8 public examples).
- `LICENSE`: MIT license and attribution notice.

The separate workspace-level `../agentsml-ideation/` folder contains research, adapter planning, conformance planning, and spec regeneration material. It is not part of the public spec package itself.

## Current Version

Specification version: `0.2.0`

The canonical schema accepts both `0.1` and `0.2` documents.

What `0.2` provides:

- A normative **condition grammar** for edge conditions and step expressions: comparisons (`==`, `!=`, `<`, `<=`, `>`, `>=`), boolean operators (`&&`, `||`, `!`), parentheses, literals, and references (`input`, `state`, `steps.<id>.output.<field>`).
- Formalized **fan-out** (one step, two or more concurrent successors) and **joins** (`join: wait_all` / `join: wait_any`), both governed by `agentsml-graph`.
- Protocol first-class citizens: **MCP** (`mcp_servers` configuration and `mcp_tool_name`), **A2A** (`a2a_agents` client bindings and `a2a_server` service exposure), and **AG-UI** streaming.
- A **step output** convention: structured object output where conditions resolve nested fields.
- **Approval semantics**: typed approval results with payload inspection and gate execution control.

Schemas:

- Canonical: [schemas/agentsml.schema.json](schemas/agentsml.schema.json)
- Version 0.2: [schemas/v0.2/agentsml.schema.json](schemas/v0.2/agentsml.schema.json)
- Version 0.1: [schemas/v0.1/agentsml.schema.json](schemas/v0.1/agentsml.schema.json)

Interactive Playground:

- Open [`docs/index.html`](docs/index.html) in any browser or deploy directly to GitHub Pages.

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
