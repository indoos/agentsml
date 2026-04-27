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
events: {}
mcp_servers: {}
a2a_agents: {}
a2a_server: {}
ui: {}
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
- `events`
- `mcp_servers`
- `a2a_agents`
- `a2a_server`
- `ui`

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
- `agentsml-payments`
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
- `a2a_agent`
- `skill`
- `input`
- `output`
- `condition`
- `depends_on`
- `retry`
- `approval`
- `events`

A step should call exactly one primary target: `agent`, `tool`, `workflow`, `a2a_agent`, or approval-only `approval`.

`a2a_agent` requires `agentsml-a2a` and identifies a remote agent declared in top-level `a2a_agents`. `skill` optionally selects a remote A2A skill.

An approval-only step is a human-control step whose only primary target is `approval`. A step that invokes an `agent`, `tool`, `workflow`, or `a2a_agent` may still include approval metadata as a gate, but compilers must preserve whether the approval occurs before execution, after execution, or as a standalone pause.

Composite steps require a profile or target extension. Compilers must emit diagnostics rather than silently choosing one target when a step declares multiple primary targets.

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

## Profile Extension Blocks

Profile extension blocks are top-level objects used by optional profiles when a capability needs shared declarations rather than per-agent or per-tool fields.

### `events`

System-level event emission and export configuration.

Fields are profile-specific. Common fields include:

- `emit`
- `export`
- `redaction`

### `mcp_servers`

Named MCP server declarations for the `agentsml-mcp` profile.

Common fields:

- `description`
- `transport`
- `command`
- `args`
- `url`
- `capabilities`
- `auth`

Tools with `source: mcp.tool` may reference these declarations with `mcp_server` and `mcp_tool_name`.

### `a2a_agents`

Named remote A2A agent declarations for the `agentsml-a2a` profile.

Common fields:

- `description`
- `agent_card_url`
- `skills`
- `auth`

Workflow steps may call these remote agents with `a2a_agent`.

### `a2a_server`

Configuration for exposing an AgentsML system or workflow as an A2A-compatible agent service.

Common fields:

- `name`
- `description`
- `version`
- `skills`
- `auth`

### `ui`

Live user-interface session configuration for the `agentsml-ui` profile.

Common fields:

- `protocol`
- `transport`
- `session_model`
- `events`
- `state_schema`

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
