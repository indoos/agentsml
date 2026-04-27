# AgentsML Object Model Draft

Status: draft v0.1 seed

## Top-Level Object

```yaml
agentsml: "0.1"
kind: AgentSystem
metadata: {}
profiles: []
models: {}
tools: {}
resources: {}
prompts: {}
agents: {}
workflows: {}
schemas: {}
policies: {}
deployments: {}
```

## `AgentSystem`

The root document describes a portable agent system.

Required fields:

- `agentsml`: AgentsML version string.
- `kind`: currently `AgentSystem`.
- `metadata.name`: stable system name.

Optional fields:

- `profiles`
- `models`
- `tools`
- `resources`
- `prompts`
- `agents`
- `workflows`
- `schemas`
- `policies`
- `deployments`

## `metadata`

Common fields:

- `name`
- `version`
- `description`
- `authors`
- `license`
- `tags`

## `profiles`

Profiles declare required AgentsML capability sets.

Examples:

- `agentsml-core`
- `agentsml-graph`
- `agentsml-conversation`
- `agentsml-rag`
- `agentsml-mcp`
- `agentsml-a2a`
- `agentsml-ui`
- `agentsml-commerce`
- `agentsml-enterprise`
- `agentsml-observability`

Compilers must emit diagnostics if a required profile is unsupported by a target.

## `model`

Portable model reference.

Fields:

- `provider`
- `name`
- `version`
- `parameters`
- `fallbacks`

Example:

```yaml
models:
  default:
    provider: openai
    name: gpt-5.1
    parameters:
      temperature: 0.2
```

## `agent`

Fields:

- `description`
- `role`
- `model`
- `instructions`
- `tools`
- `resources`
- `prompts`
- `memory`
- `knowledge`
- `output_schema`
- `policies`
- `events`

Example:

```yaml
agents:
  researcher:
    role: researcher
    model: default
    instructions: "Research the topic and cite sources."
    tools: [web_search]
```

## `tool`

Fields:

- `description`
- `source`
- `input_schema`
- `output_schema`
- `auth`
- `permissions`
- `side_effect`
- `timeout`
- `error_policy`

Tool sources:

- `local.function`
- `mcp.tool`
- `openapi.operation`
- `asyncapi.operation`
- `builtin`
- `target.native`

## `resource`

Resources provide context or data but are not necessarily callable.

Fields:

- `description`
- `source`
- `schema`
- `auth`
- `permissions`

## `prompt`

Reusable prompt template.

Fields:

- `description`
- `template`
- `input_schema`
- `metadata`

## `memory`

Fields:

- `session`
- `checkpoint`
- `long_term`
- `retention`
- `storage`

## `knowledge`

Fields:

- `knowledge_base`
- `retriever`
- `citation_policy`
- `document_store`
- `index`

Usually belongs to `agentsml-rag`.

## `workflow`

Fields:

- `description`
- `input_schema`
- `output_schema`
- `state`
- `steps`
- `edges`
- `events`
- `error_policy`

Simple sequential workflows may omit `edges` and rely on step order.

## `step`

Fields:

- `id`
- `agent`
- `tool`
- `workflow`
- `input`
- `output`
- `condition`
- `depends_on`
- `retry`
- `approval`
- `events`

A step should call exactly one of `agent`, `tool`, or `workflow` unless a profile explicitly permits composite steps.

## `edge`

Fields:

- `from`
- `to`
- `condition`
- `label`

Cycles require `agentsml-graph`.

## `state`

Fields:

- `schema`
- `initial`
- `scope`
- `reducers`

Reducers are required when parallel branches can update the same state key.

## `event`

Core event categories:

- `run.started`
- `run.finished`
- `run.error`
- `step.started`
- `step.finished`
- `message.delta`
- `tool.call`
- `tool.result`
- `state.snapshot`
- `state.delta`
- `human.input_required`
- `artifact.created`

## `policy`

Fields:

- `description`
- `applies_to`
- `permissions`
- `guardrails`
- `approval`
- `audit`

## `human_approval`

Fields:

- `prompt`
- `input_schema`
- `approvers`
- `timeout`
- `on_approve`
- `on_reject`
- `audit`

## `artifact`

Fields:

- `type`
- `uri`
- `schema`
- `metadata`
- `provenance`

## `deployment`

Fields:

- `target`
- `runtime`
- `environment`
- `secrets`
- `observability`
- `scaling`
