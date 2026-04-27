# AgentsML Execution Semantics Draft

Status: draft v0.1 seed

## Run Lifecycle

An AgentsML runtime or compiler should model execution as a run:

1. Validate AgentsML document.
2. Resolve profiles and target capabilities.
3. Resolve model, tool, resource, prompt, agent, and workflow references.
4. Validate input against workflow input schema.
5. Initialize run state.
6. Execute steps according to workflow order or graph edges.
7. Emit normalized events.
8. Produce outputs and artifacts.
9. Persist trace, diagnostics, and optional checkpoints.

## Step Execution

A step invokes exactly one primary target:

- `agent`
- `tool`
- `workflow`
- `a2a_agent`
- approval-only `approval`

Composite targets require a profile or target extension.

An approval-only step pauses the run and returns a typed approval result. A step that also invokes an `agent`, `tool`, `workflow`, or `a2a_agent` may include approval metadata as a gate around that invocation, but the invocation remains the primary target.

## State Mutation

Steps do not mutate state implicitly.

A step returns an output. The workflow maps that output into state through target-specific adapter code or explicit AgentsML output bindings.

Parallel branches updating the same state key require a reducer.

## Branching

Simple conditions may be in core.

Arbitrary graph routing, multi-path fan-out, joins, and cycles require `agentsml-graph`.

## Retries

AgentsML distinguishes:

- validation retry
- model retry
- tool retry
- workflow step retry
- graph loop retry

Compilers must not silently collapse these categories when a target treats them differently.

## Interrupts And Human Approval

Human approval pauses a run with:

- typed approval payload
- approver identity requirements
- approve/reject/resume paths
- timeout behavior
- audit event

Resume semantics are target-specific and must be declared in diagnostics when lossy.

## Events

Execution should emit normalized events for:

- run lifecycle
- step lifecycle
- messages
- tool calls
- state snapshots/deltas
- human input
- artifacts
- diagnostics

## Failure

Failures should produce structured diagnostics and a terminal or resumable run state.

Targets should distinguish:

- validation failure
- target capability failure
- runtime failure
- tool failure
- policy failure
- human rejection
