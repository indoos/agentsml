# Tutorial: One Spec, Five Frameworks

One AgentsML document can describe an agent system that runs on several agent frameworks. This tutorial takes one realistic spec, a refund agent with a tool, a two-step workflow, and v0.3 features, and compiles it to five targets:

- `langgraph` (Python)
- `openai-agents` (Python)
- `google-adk` (Python)
- `crewai` (Python)
- `mastra` (TypeScript)

For each target you will see the key generated code, the diagnostics the compiler prints, and how the target supports each feature. Read the [quickstart](quickstart.md) first if you have not installed the CLI.

Every command and output below was run against the published package `agentsml-impl` 0.2.2 with the public example [`resilient-agent.agentsml.yaml`](https://github.com/indoos/agentsml/blob/main/examples/resilient-agent.agentsml.yaml).

## The spec

The example declares the three v0.3 features this tutorial exercises:

- **Tool approval.** The `issue_refund` tool has `needs_approval: true` and `approval_mode: per_arguments`. A refund is a `payment` side effect, so the run pauses until someone approves that exact argument set.
- **Step retry, timeout, and fallback.** The `assess` step has `timeout: 60s`, up to three attempts with exponential backoff, and a static fallback output if it times out. The `refund` step has its own timeout and a retry policy.
- **Agent reasoning.** The `analyst` agent sets `reasoning: {effort: medium, budget_tokens: 4096}`.

The workflow is `assess` → `manager_review` (a human approval gate) → `refund`. Here is the tool and the first step, trimmed:

```yaml
tools:
  issue_refund:
    source: local.function
    side_effect: payment
    needs_approval: true
    approval_mode: per_arguments
    input_schema: {...}   # order_id: string, amount: number
agents:
  analyst:
    reasoning:
      effort: medium
      budget_tokens: 4096
      expose_trace: false
workflows:
  main:
    steps:
      - id: assess
        agent: analyst
        timeout: 60s
        retry:
          max_attempts: 3
          backoff: exponential
          initial_interval: 2s
          max_interval: 30s
          on_timeout: fallback
        fallback:
          output:
            summary: Assessment timed out; route to manual review.
            eligible: false
```

## Step 1: Validate and doctor

Copy the example into a scratch directory so the outputs stay out of the repo:

```bash
mkdir tutorial && cd tutorial
cp /path/to/agentsml/examples/resilient-agent.agentsml.yaml .
agentsml validate resilient-agent.agentsml.yaml
```

Observed output:

```text
Validating resilient-agent.agentsml.yaml

✓ Valid — no diagnostics
  agents=2, tools=1, workflows=1
```

Next, ask each target what it can express. Doctor prints a capability table per target. Here is the subset of rows this tutorial depends on, taken from the observed doctor output:

| Feature | `langgraph` | `openai-agents` | `google-adk` | `crewai` | `mastra` |
|---|---|---|---|---|---|
| graph_edges | native | lossy | lossy | lossy | native |
| graph_conditions | native | manual | manual | manual | native |
| human_approval | native | adapter | manual | adapter | adapter |
| tool_approval | native | native | native | adapter | adapter |
| retry | native | adapter | adapter | adapter | native |
| on_timeout | native | adapter | adapter | adapter | adapter |
| reasoning | adapter | native | native | adapter | adapter |

Run it for any target with `agentsml doctor resilient-agent.agentsml.yaml --target <name>`. The graph rows match the **Graph edges** and **Graph conditions** columns of [`agentsml-impl/docs/target-support.md`](https://github.com/indoos/agentsml-impl/blob/main/docs/target-support.md). The v0.3 rows are declared per target in each `capabilities.yaml`, which is what `doctor` reads. At the time of writing, the repo manifests and the 0.2.2 doctor output agree for these five targets.

`crewai` also prints an error in doctor, which you should read before using it:

```text
  ERROR  (profiles.required): Target 'crewai' does not support required profile
'agentsml-graph'.
```

The example requires the `agentsml-graph` profile because it has a multi-step graph with approval gates. CrewAI does not support that profile. Compilation still succeeds, so treat CrewAI output for this spec as a starting point that needs review, not a faithful port.

## Step 2: Compile to each target

```bash
agentsml compile resilient-agent.agentsml.yaml --target langgraph --out tut-langgraph
agentsml compile resilient-agent.agentsml.yaml --target openai-agents --out tut-openai-agents
agentsml compile resilient-agent.agentsml.yaml --target google-adk --out tut-google-adk
agentsml compile resilient-agent.agentsml.yaml --target crewai --out tut-crewai
agentsml compile resilient-agent.agentsml.yaml --target mastra --out tut-mastra
```

Each command writes `tut-<target>/resilient_refund_agent/<target>/`. The diagnostics below are copied from the compile output.

### langgraph (native graph, native retry)

Snippet from `src/resilient_refund_agent/graph.py`. The `assess` node gets the timeout wrapper and a `RetryPolicy`, and the approval gate becomes an interrupt:

```python
graph.add_node("assess", with_timeout("assess", with_step_output("assess", analyst_node), 60, "fallback", fallback_output=({'summary': 'Assessment timed out; route to manual review.', 'eligible': False},)), retry_policy=RetryPolicy(max_attempts=3, backoff_factor=2.0, initial_interval=2.0, max_interval=30.0), timeout=61)
graph.add_node("manager_review", manager_review_approval)
```

Tool approval is enforced by `guarded_tool_node`, driven by `TOOL_APPROVAL_POLICY = {'issue_refund': 'per_arguments'}`.

Diagnostics:

```text
  WARNING  (models.default.reasoning): reasoning.budget_tokens/expose_trace has
no openai model kwarg in the generated LangGraph code and is dropped.
  WARNING  (workflows.main.steps.refund.retry.backoff): Step 'refund' uses
linear backoff; LangGraph RetryPolicy supports only a constant or geometric
factor, so a constant interval is generated.
```

### openai-agents (native tool approval, adapter retry)

Snippet from `src/resilient_refund_agent/agent.py`. Tool approval maps directly to the SDK's `needs_approval`, and reasoning effort maps to `Reasoning`:

```python
issue_refund_tool = function_tool(tools.issue_refund, name_override='issue_refund', needs_approval=approval_gate("issue_refund"))

analyst_agent = Agent(
    name="analyst",
    model='gpt-5.1',
    model_settings=ModelSettings(temperature=0.1, reasoning=Reasoning(effort='medium')),
    ...
```

Retry and timeout are not native here. `workflow.py` wraps each step in a generated `with_resilience(...)` call with `max_attempts=3`, `backoff='exponential'`, `timeout=60`, and `on_timeout='fallback'`. Tool approvals are resolved by `run_with_approvals(...)`, which takes an `approver` callback that you supply.

Diagnostics:

```text
  WARNING  (agents.analyst.reasoning.budget_tokens): Agent 'analyst'
reasoning.budget_tokens has no OpenAI Responses equivalent (only effort levels)
and is dropped.
  WARNING  (profiles.required): Target 'openai-agents' supports required profile
'agentsml-graph' with lossy mapping.
  WARNING  (workflows.main.steps.manager_review): Step 'manager_review' is not
an agent step and is skipped by the generated sequential workflow.
  INFO  (steps.approval): Target does not natively support human approval (HITL)
steps. (generated adapter code required)
```

The skipped `manager_review` warning matters: the generated sequential workflow has no pause for the manager, so the manager approval step is not enforced by the generated code. Only the tool-level approval is enforced, and only if you pass an `approver` to `run_with_approvals`.

### google-adk (native tool approval, manual human approval)

Snippet from `agent.py`. The tool is wrapped in a `before_tool_callback` that implements `per_arguments` approvals, and the analyst's reasoning is not applied because the model is LiteLLM:

```python
TOOL_APPROVAL_POLICY = {'issue_refund': 'per_arguments'}

refund_inner_agent = LlmAgent(
    ...
    model=LiteLlm(model="openai/gpt-5.1"),
    before_tool_callback=_approval_gate,
    ...
)
```

Diagnostics:

```text
  WARNING  (agents.analyst.reasoning): Agent 'analyst' declares reasoning
settings, but ADK's BuiltInPlanner thinking config only applies to Gemini models
and model 'default' uses LiteLlm; reasoning is not applied.
    → Use a Gemini model or pass provider thinking kwargs to LiteLlm manually.
  WARNING  (profiles.required): Target 'google-adk' supports required profile
'agentsml-graph' with lossy mapping.
  WARNING  (workflows.main): Human approval steps require a custom
before_tool_callback in Google ADK. Vertex AI human-in-the-loop integration
recommended.
    → Implement a before_tool_callback for approval gates.
  WARNING  (workflows.main.steps.refund.timeout): Step 'refund' has a timeout
and its agent uses tools that need approval: approval wait time counts toward
the step timeout.
  INFO  (steps.approval): Target does not natively support human approval (HITL)
steps. (requires manual configuration)
```

### crewai (adapter approval and retry, graph profile error)

Snippet from `crew.py`. Each step becomes a `PolicyTask` with the retry and timeout fields, and the tool is wrapped by `requires_approval`:

```python
@tool
@requires_approval('issue_refund', 'per_arguments')
def issue_refund(order_id: str, amount: float) -> dict[str, Any]:
```

```python
assess = PolicyTask(
    ...
    policy_max_attempts=3,
    policy_backoff='exponential',
    policy_on_timeout='fallback',
    policy_timeout=60.0,
    policy_has_fallback_output=True,
    ...
)
```

`PolicyTask` is a generated `Task` subclass in `policy.py`, not a CrewAI built-in.

Diagnostics:

```text
  ERROR  (profiles.required): Target 'crewai' does not support required profile
'agentsml-graph'.
  WARNING  (agents.analyst.reasoning): reasoning.expose_trace/budget_tokens has
no CrewAI LLM setting for provider 'openai' and is dropped.
  WARNING  (workflows.main.steps.refund.timeout): Step 'refund' has a timeout
and its agent uses tools that need approval: approval wait time counts toward
the step timeout.
  INFO  (steps.approval): Target does not natively support human approval (HITL)
steps. (generated adapter code required)
```

### mastra (native retry and graph, adapter approval)

Snippet from `src/workflow.ts`. Retry maps to Mastra's `retries` on the step, with backoff computed inside the step. Tool approval uses `requireApproval` on the tool:

```typescript
const assessStep = createStep({
  id: "assess",
  ...
  retries: 2,   // max_attempts 3
  ...
});
```

```typescript
export const issueRefundTool = createTool({
  id: "issue_refund",
  inputSchema: z.object({ order_id: z.string(), amount: z.number() }),
  requireApproval: (input) => needsApproval("issue_refund", 'per_arguments', input),
  execute: async (inputData) => {
    recordApproval("issue_refund", 'per_arguments', inputData);
```

Diagnostics:

```text
  WARNING  (agents.analyst.reasoning): reasoning.budget_tokens has no openai
provider option in the generated Mastra agent (only reasoningEffort) and is
dropped.
  WARNING  (workflows.main.steps.refund.timeout): Step 'refund' has a timeout
and its agent uses tools that need approval: approval wait time counts toward
the step timeout.
  INFO  (agents): Multi-agent project detected. Generating a Mastra supervisor
agent with sub-agents.
  INFO  (steps.approval): Target does not natively support human approval (HITL)
steps. (generated adapter code required)
```

Mastra also generates `src/supervisor.ts`, a supervisor agent that routes between `analyst` and `refunder`.

## Step 3: Native, adapter, lossy, manual

The capability levels mean the following:

- **native**: the target has a direct construct for the feature, and the generated code uses it. Example: LangGraph's `RetryPolicy` for step retry.
- **adapter**: the target has no direct construct, so the compiler generates wrapper code (a callback, a wrapper class, or a helper) that implements the feature. The behavior matches the spec, but the code is yours to maintain.
- **manual**: the compiler emits a stub or a note and you complete the feature yourself. Example: Google ADK's human approval gate.
- **lossy**: the target can express an approximation of the feature, and the compiler warns about what is changed. Example: LangGraph's linear backoff becomes a constant interval, and `budget_tokens` is dropped on OpenAI.
- **unsupported**: no mapping exists. The compiler reports it as an error or a warning.

Use the diagnostics to find lossy and manual spots, then decide whether each approximation is acceptable for your system. The compile output reports the approximations the compiler knows about as `WARNING` or `INFO` lines, so read them all before you ship.

## What to take away

- The same spec compiled to five targets. The approval, retry, timeout, and reasoning features are all present in the output, but how faithfully each one lands varies by target.
- LangGraph and Mastra have native graph and retry support, so they are the closest matches for this spec.
- OpenAI Agents and Google ADK do native tool approval but need work for the human gate and the retry policy.
- CrewAI reports a profile error. Use it only after reviewing the diagnostics.

Next, run `agentsml doctor` on your own spec for the target you care about, and read the `diagnostics.yaml` file in the generated project for the full list of portability notes.
