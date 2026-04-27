# AgentsML Observability Draft

Status: draft v0.1 seed

## Goals

AgentsML should make agent runs inspectable, replayable where possible, and portable across observability systems.

## Event Alignment

AgentsML events should be mappable to CloudEvents-style envelopes when exported.

Core event fields:

- `id`
- `type`
- `source`
- `time`
- `run_id`
- `workflow_id`
- `step_id`
- `agent_id`
- `tool_id`
- `data`

## Trace Alignment

AgentsML traces should align with OpenTelemetry:

- run as trace
- workflow as span
- step as span
- model call as span
- tool call as span
- approval wait as span

## Recommended Span Attributes

- `agentsml.version`
- `agentsml.profile`
- `agentsml.workflow.id`
- `agentsml.step.id`
- `agentsml.agent.id`
- `agentsml.tool.id`
- `agentsml.model.provider`
- `agentsml.model.name`
- `agentsml.target`
- `agentsml.diagnostic.count`

## Redaction

Observability config should declare redaction policy for:

- prompts
- tool arguments
- tool outputs
- user data
- secrets
- payment data
- retrieved documents

