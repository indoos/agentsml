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

## Retry and timeout semantics (v0.3)

A step `retry` policy governs workflow step retry only.

- **Attempt counting**: `max_attempts` counts all attempts including the first; `max_attempts: 1` means no retry. `timeout` applies to each attempt separately.
- **Backoff**: the delay before attempt n+1 is `initial_interval` for `none` and `linear` (linear adds `initial_interval` per attempt), `initial_interval * 2^(n-1)` for `exponential`, capped by `max_interval`. Backoff is a compiler-implemented policy: no framework exposes declarative step-level backoff, so targets without native support must emit `lossy_mapping` and may approximate.
- **`on_timeout`**: `error` fails the attempt (and is retried while attempts remain); `return_to_model` returns a timeout result to the calling model instead of failing; `fallback` uses the step `fallback` declaration (see object-model.md): its `output` value is returned as the step output, else the step is re-run once with `fallback.model` under the same `timeout` (a second timeout fails the step), else the step output is an empty JSON object with an `info` diagnostic. Targets without the behaviour must emit `lossy_mapping`.
- **LangGraph**: enforces `timeout` natively. A timed step is generated as an `async def` node passed to `add_node(..., timeout=<seconds>)` (LangGraph 1.2.20 rejects node timeouts on sync nodes, so the runner uses `ainvoke`), and the node retry policy retries `NodeTimeoutError` while attempts remain. All three `on_timeout` modes are honoured: `error` propagates `NodeTimeoutError`; `return_to_model` appends the message `step <id> timed out after <n>s` to `messages` and records it as the step output; `fallback` returns the step's fallback output, which is the declared `fallback.output` (also appended as an `AIMessage`), or the result of re-running the agent call with `fallback.model` under the same deadline, or an empty JSON object (with an `info` diagnostic) when the step declares no `fallback`. An unparseable `timeout` still emits `lossy_mapping`.
- **Approvals**: time spent waiting for human approval does not count against `timeout` and a pending approval is never retried. A rejected approval is final and does not consume attempts. Retries of a gated step re-use the existing approval decision unless the tool `approval_mode` is `always`.
- **Other targets (retry, timeout, fallback)**: fifteen targets declare `retry` and `on_timeout`: AG2, Agno, Claude Agent SDK, CrewAI, Google ADK, LangChain, LlamaIndex, Microsoft Agent Framework, OpenAI Agents, PydanticAI, smolagents, Strands Agents and Vercel AI SDK declare `retry: adapter` and `on_timeout: adapter`; Mastra declares `retry: native` (`max_attempts - 1` becomes `createStep({ retries })`, with backoff computed in the step) and `on_timeout: adapter` (a `Promise.race` wrapper). LangGraph is the only native `on_timeout` target (see above). Every adapter target generates a per-step wrapper that applies the deadline per attempt, retries with the declared backoff, and on the final timeout honours `error`, `return_to_model` (message `step <id> timed out after <n>s`) and `fallback` with the same precedence as LangGraph. Notable mechanisms: `asyncio.wait_for` wrappers (OpenAI Agents, LangChain, LlamaIndex, Strands Agents; Google ADK wraps the step in a `_GuardedStepAgent`), a `PolicyTask` over `Task.execute_sync` (CrewAI), `run_step` wrappers (Agno, smolagents), a `step_runtime` wrapper (PydanticAI), `with_resilience` wrappers (Claude Agent SDK, Microsoft Agent Framework), a generated coordinator tool (AG2), and `src/workflow.ts` (Vercel AI SDK). Native framework retry settings are generally not used because they lack backoff, caps, timeouts or fallback. A timed-out attempt in a Python target is abandoned or cancelled best effort rather than killed, so a synchronous tool already running may still complete. Approval waits are excluded from the deadline in every adapter target whose manifest describes the behaviour (all of the above except LangChain, whose manifest is silent on it); a target that cannot exclude them must emit `lossy_mapping` when a timed step uses an approval-gated tool. Targets that do not declare these keys (including spring-ai and the cloud and export targets) emit `lossy_mapping`.
- **Tool timeout**: a tool's `timeout` bounds one execution of the tool body only; time spent waiting for that call's approval is not counted. When it expires the model receives the tool result `tool <name> timed out after <n>s` and the run continues; the abandoned body's later result is discarded (a synchronous body already running in a worker thread cannot be interrupted, so its side effects may still complete). All fifteen code targets that map v0.3 enforce it; an unparseable or non-positive value emits `lossy_mapping` at `tools.<key>.timeout`.
- **Tool approval**: a tool's `needs_approval` / `approval_mode` is honoured only by targets whose manifest declares `tool_approval: native|adapter`. In every enforcing target the tool never runs without an explicit approval: the run either pauses for a decision or, in generated runners without an approval handler or terminal, rejects; a rejection returns a message to the model. Targets whose manifest does not declare `tool_approval` (including spring-ai and the cloud and export targets) cannot enforce it and emit `lossy_mapping` per tool, so the author must gate the tool manually; declaring `needs_approval` satisfies the unsafe-side-effect check but does not by itself guarantee enforcement.
  - Native (the framework has an approval or interrupt primitive): LangGraph calls a graph `interrupt({"type": "tool_approval", "tool", "args"})` in the generated tool node before running the tool (`always`, `once_per_session` per thread, `per_arguments` per canonical-JSON argument hash) and returns a rejection tool message otherwise; it requires the checkpointer the generated graph already provides. LangChain uses `HumanInTheLoopMiddleware` with a generated resume loop. OpenAI Agents uses `function_tool(needs_approval=...)` and resolves `RunResult.interruptions` through `RunState.approve`/`reject`. Google ADK uses `FunctionTool(require_confirmation=True)` for `always` and a generated `before_tool_callback` with `ToolContext.request_confirmation` for the other modes. Agno uses `@tool(requires_confirmation=True)` and resumes with `Agent.continue_run`.
  - Adapter (generated gate code around the tool or call): CrewAI (approval decorator), smolagents (approval decorator), LlamaIndex (gate using `InputRequiredEvent`/`HumanResponseEvent`), Microsoft Agent Framework (Semantic Kernel function-invocation filter), AG2 (`approval_gate` middleware), Strands Agents (`BeforeToolCallEvent` hook raising an interrupt), Claude Agent SDK (generated tool loop that gates each `tool_use` block), Mastra (`createTool({ requireApproval })` with suspend/approve), PydanticAI (deferred tools with a generated grant set), Vercel AI SDK (`needs_approval` predicate with a generated grant set and runtime). `once_per_session` and `per_arguments` memory is generated where the framework has no equivalent.
  - Workflow-step `approval` is separate and is not enforced by tool gates; for example Google ADK still needs a custom callback or external gate for it.
- **Unsupported targets**: a target manifest declares `retry` (and `reasoning`) support; absence is treated as lossy and produces `lossy_mapping` diagnostics.

## Limits, handoffs and tool isolation (Draft 0.4)

- **`limits.max_turns`**: the number of model requests one invocation of the agent may make, counting every model call including those triggered by tool results. Time spent waiting for approval does not count. When the limit would be exceeded the invocation fails with an error of kind `limit_exceeded`. This is a step failure, but `limit_exceeded` is never retried: step `retry` does not apply to it. The step `fallback` (`output` or `model`) applies as for any other failed step.
- **`handoffs`**: during its run the agent may transfer control to one listed agent. The receiving agent continues the same conversation (it sees the prior messages) and its final output becomes the output of the step that invoked the original agent. Handoff targets need not appear as workflow steps. A handoff counts as a turn of the receiving agent for that agent's own `limits`. Every referenced key must be a defined agent (otherwise the compiler reports `ambiguous_reference`) and an agent may not hand off to itself. Cycles between agents are allowed and are bounded by `limits`.
- **Portable lowering of handoffs**: a target without native handoffs may lower a handoff to an agent-as-tool call, where the receiving agent runs with the conversation and returns its output. If conversation continuity is lost in that lowering the target must emit `lossy_mapping`.
- **Tool `isolation`**: `thread` (default) keeps v0.3 behavior: a timed-out synchronous body may keep running in the background and its result is discarded. `process` runs the tool body in a separate OS process; arguments and results must be JSON-serializable. When the tool `timeout` expires the process is terminated, so the body's side effects stop. `isolation` without `timeout` is valid and process isolation still applies. Targets that cannot isolate a tool body must emit `lossy_mapping` at `tools.<key>.isolation`.
- Targets that do not implement these fields must emit `lossy_mapping`; this draft does not require any target to implement them yet.

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
