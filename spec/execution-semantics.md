# AgentsML Execution Semantics Specification

Status: Specification v0.2

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

## Retry and timeout semantics (Draft 0.3)

A step `retry` policy governs workflow step retry only.

- **Attempt counting**: `max_attempts` counts all attempts including the first; `max_attempts: 1` means no retry. `timeout` applies to each attempt separately.
- **Backoff**: the delay before attempt n+1 is `initial_interval` for `none` and `linear` (linear adds `initial_interval` per attempt), `initial_interval * 2^(n-1)` for `exponential`, capped by `max_interval`. Backoff is a compiler-implemented policy: no framework exposes declarative step-level backoff, so targets without native support must emit `lossy_mapping` and may approximate.
- **`on_timeout`**: `error` fails the attempt (and is retried while attempts remain); `return_to_model` returns a timeout result to the calling model instead of failing; `fallback` uses the step `fallback` declaration (see object-model.md): its `output` value is returned as the step output, else the step is re-run once with `fallback.model` under the same `timeout` (a second timeout fails the step), else the step output is an empty JSON object with an `info` diagnostic. Targets without the behaviour must emit `lossy_mapping`.
- **LangGraph**: enforces `timeout` natively. A timed step is generated as an `async def` node passed to `add_node(..., timeout=<seconds>)` (LangGraph 1.2.20 rejects node timeouts on sync nodes, so the runner uses `ainvoke`), and the node retry policy retries `NodeTimeoutError` while attempts remain. All three `on_timeout` modes are honoured: `error` propagates `NodeTimeoutError`; `return_to_model` appends the message `step <id> timed out after <n>s` to `messages` and records it as the step output; `fallback` returns the step's fallback output, which is the declared `fallback.output` (also appended as an `AIMessage`), or the result of re-running the agent call with `fallback.model` under the same deadline, or an empty JSON object (with an `info` diagnostic) when the step declares no `fallback`. An unparseable `timeout` still emits `lossy_mapping`.
- **Approvals**: time spent waiting for human approval does not count against `timeout` and a pending approval is never retried. A rejected approval is final and does not consume attempts. Retries of a gated step re-use the existing approval decision unless the tool `approval_mode` is `always`.
- **Other targets (retry, timeout, fallback)**: OpenAI Agents, Google ADK, CrewAI and Mastra declare `retry` and `on_timeout` (`adapter`, except Mastra `retry: native`, which maps `max_attempts - 1` to `createStep({ retries })`). Each generates a per-step wrapper that applies the deadline per attempt, retries with the declared backoff, and on the final timeout honours `error`, `return_to_model` (message `step <id> timed out after <n>s`) and `fallback` with the same precedence as LangGraph. A timed-out attempt in a Python target is abandoned rather than killed, so its side effects may still complete. OpenAI Agents keeps tool-approval waits outside the deadline; Google ADK, CrewAI and Mastra count them toward it and emit `lossy_mapping` when a timed step uses an approval-gated tool.
- **Tool approval**: a tool's `needs_approval` / `approval_mode` is honoured only by targets whose manifest declares `tool_approval: native|adapter`. LangGraph enforces it natively: the generated tool node calls a graph `interrupt({"type": "tool_approval", "tool", "args"})` before running the tool (`always`, `once_per_session` per thread, `per_arguments` per canonical-JSON argument hash) and returns a rejection tool message when the decision is not approval; it requires the checkpointer the generated graph already provides. OpenAI Agents uses the SDK's native `function_tool(needs_approval=...)` and resolves `RunResult.interruptions` through `RunState.approve`/`reject`; Google ADK uses `FunctionTool(require_confirmation=True)` for `always` and a generated `before_tool_callback` with `ToolContext.request_confirmation` for the other modes; Mastra uses `createTool({ requireApproval })` with the agent suspend/approve flow; CrewAI wraps the tool function in a generated approval decorator. In every enforcing target the tool never runs without an explicit approval: the run either pauses for a decision or, in generated runners without an approval handler or terminal, rejects; a rejection returns a message to the model. Targets whose manifest does not declare `tool_approval` cannot enforce it and emit `lossy_mapping` (the compiler emits it per tool), so the author must gate the tool manually; declaring `needs_approval` satisfies the unsafe-side-effect check but does not by itself guarantee enforcement.
- **Unsupported targets**: a target manifest declares `retry` (and `reasoning`) support; absence is treated as lossy and produces `lossy_mapping` diagnostics.

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
