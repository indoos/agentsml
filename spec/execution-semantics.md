# AgentsML Execution Semantics Draft

Status: draft v0.2

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

### Step Outputs

A step output is a structured object. When a step result is read by a condition, the
step must produce an object so that condition fields resolve. A step that returns
free text is stored as `{ "text": <value> }`.

Implementations may prompt a model for a JSON object when a later condition reads
that step's output. This is a target-side convenience and does not change the
document semantics.

## Branching

Simple conditions may be in core.

Arbitrary graph routing, multi-path fan-out, joins, and cycles require `agentsml-graph`.

### Condition Grammar

An edge condition is a string expression. Core supports:

- comparisons: `==`, `!=`, `<`, `<=`, `>`, `>=`
- boolean operators: `&&`, `||`, `!`
- parentheses
- string, number, boolean, and null literals
- dotted and indexed references

A reference has one of three roots:

- `input` — the workflow input
- `state` — the workflow state
- `steps` — step outputs, addressed as `steps.<step_id>.output.<field>`

Expressions are written inside `${ ... }`. Implementations must reject expressions
outside this grammar rather than evaluating them as code, and must report a
diagnostic when a condition cannot be parsed. A condition that cannot be parsed is
never taken.

### Branch Selection

Every outgoing edge of a step is evaluated. Each edge whose condition holds is
taken, so several matching edges may be taken at once. An edge without a condition
is always taken. A step with no taken successor ends that branch of the run.

### Fan-Out And Joins

- **Fan-out** is one step with two or more unconditional successors. The successors
  may run concurrently.
- **Join** is one step with two or more unconditional predecessors. The step waits
  for all of them and runs once.

Both require the `agentsml-graph` profile. Conditional alternatives between two
successors are a single-path decision and remain in core.

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

The pause carries a payload describing what is being approved: the step, the reason,
and any approval metadata from the document.

Resume semantics are target-specific and must be declared in diagnostics when lossy.
A resumed run supplies a decision. The decision becomes a typed approval result,
which is available to later steps. A rejected decision must not execute the gated
invocation.

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
