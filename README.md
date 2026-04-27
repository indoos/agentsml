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

Draft version: `0.1`

Schema:

- [schemas/agentsml.schema.json](schemas/agentsml.schema.json)

## Example Documents

- [simple-agent.agentsml.yaml](examples/simple-agent.agentsml.yaml)
- [credit-risk-agent.agentsml.yaml](examples/credit-risk-agent.agentsml.yaml)
- [fraud-detection-agent.agentsml.yaml](examples/fraud-detection-agent.agentsml.yaml)
- [kyc-aml-investigation-agent.agentsml.yaml](examples/kyc-aml-investigation-agent.agentsml.yaml)

## License

MIT License.

Copyright (c) 2026 Impetus Technologies

Author: Sanjay Sharma
