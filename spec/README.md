# AgentsML Specification v0.2

This folder contains the canonical specification chapters for AgentsML v0.2.

Companion artifacts:

- Schemas:
  - Canonical: [`../schemas/agentsml.schema.json`](../schemas/agentsml.schema.json)
  - Version 0.2: [`../schemas/v0.2/agentsml.schema.json`](../schemas/v0.2/agentsml.schema.json)
  - Version 0.1: [`../schemas/v0.1/agentsml.schema.json`](../schemas/v0.1/agentsml.schema.json)
- Examples: [`../examples/`](../examples/)
- Web Playground & Docs: [`../docs/index.html`](../docs/index.html)

Specification chapters:

- [`object-model.md`](object-model.md) — Portable agent system declarations and core object model.
- [`execution-semantics.md`](execution-semantics.md) — Run lifecycle, branching, graph fan-out/joins, approvals, and condition grammar.
- [`profiles.md`](profiles.md) — Capability profiles (`core`, `graph`, `mcp`, `a2a`, `ui`, `rag`, `payments`).
- [`diagnostics.md`](diagnostics.md) — Standard diagnostic codes and error handling contracts.
- [`security-permissions.md`](security-permissions.md) — Tool permissions, side-effect controls, and human-in-the-loop policies.
- [`observability.md`](observability.md) — Normalized event telemetry and trace mappings.
