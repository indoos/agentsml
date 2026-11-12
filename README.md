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

- [simple-agent.agentsml.yaml](examples/simple-agent.agentsml.yaml)
- [credit-risk-agent.agentsml.yaml](examples/credit-risk-agent.agentsml.yaml)
- [fraud-detection-agent.agentsml.yaml](examples/fraud-detection-agent.agentsml.yaml)
- [kyc-aml-investigation-agent.agentsml.yaml](examples/kyc-aml-investigation-agent.agentsml.yaml)
- [branching-agent.agentsml.yaml](examples/branching-agent.agentsml.yaml) — draft 0.2: conditional edges, fan-out, and a join.

## License

MIT License.

Copyright (c) 2026 Impetus Technologies

Author: Sanjay Sharma
