# AgentsML Quickstart

This guide takes you from zero to a running agent in about five minutes. All output below comes from the published package `agentsml-impl` (PyPI, version 0.2.2 at the time of writing).

## 1. Install

Requires Python 3.11 or newer. Pick one:

```bash
# Option A: run without installing; in the commands below, replace `agentsml` with `uvx --from agentsml-impl agentsml`
uvx --from agentsml-impl agentsml --help

# Option B: install it into the current environment (pip)
pip install agentsml-impl
agentsml --help
```

## 2. Write an agent

Create `hello-agent.agentsml.yaml`:

```yaml
agentsml: "0.2"
kind: AgentSystem
metadata:
  name: hello-agent
  version: 0.1.0
  description: Minimal single-agent quickstart.
profiles:
  - agentsml-core
models:
  default:
    provider: openai
    name: gpt-5.1
    parameters:
      temperature: 0.2
agents:
  helper:
    description: Answers questions briefly.
    role: assistant
    model: default
    instructions: Answer the user's question in two sentences or fewer.
workflows:
  main:
    description: Answer one question.
    input_schema:
      type: object
      properties:
        question:
          type: string
      required:
        - question
    steps:
      - id: answer
        agent: helper
        input:
          question: ${input.question}
```

`models` names the model, `agents` defines who does the work, and `workflows.main.steps` says what runs. `${input.question}` reads the value passed in at run time.

## 3. Validate

```bash
agentsml validate hello-agent.agentsml.yaml
```

Observed output:

```text
Validating hello-agent.agentsml.yaml

✓ Valid — no diagnostics
  agents=1, tools=0, workflows=1
```

If a step names an agent that does not exist (`agent: ghost`), validation fails with exit code 1:

```text
  ERROR  (workflows.main.steps.answer.agent): Step 'answer' references undefined
agent 'ghost'.
```

## 4. Check a target with doctor

`doctor` asks whether this document can be expressed on a given target. Each feature is reported as `native`, `adapter` (generated glue code), `manual` (you finish it by hand), `lossy` (approximated), or `unsupported`.

```bash
agentsml doctor hello-agent.agentsml.yaml --target langgraph
```

Observed output (abridged):

```text
Doctor: hello-agent.agentsml.yaml → langgraph
  agents              native
  retry               native
  reasoning           adapter
  ...
✓ Doctor complete — no diagnostics
```

## 5. Compile

`compile` (also available as `generate`) writes runnable target code. `-t` picks the target and `-o` the output directory.

```bash
agentsml compile hello-agent.agentsml.yaml --target langgraph --out out-langgraph
```

Observed output:

```text
Generate: hello-agent.agentsml.yaml → langgraph → out-langgraph

✓ Generated 6 files → out-langgraph/hello_agent/langgraph
  pyproject.toml
  src/hello_agent/state.py
  src/hello_agent/graph.py
  src/hello_agent/run.py
  src/hello_agent/__init__.py
  README.md
```

Output goes to `<out>/<package>/<target>/`. `graph.py` holds the LangGraph `StateGraph`, `run.py` the `python -m` entry point, and `diagnostics.yaml` the portability warnings (empty here). Re-running `compile` overwrites generated code, so keep your own changes in separate modules.

## 6. Run it

```bash
cd out-langgraph/hello_agent/langgraph
pip install -e .
export OPENAI_API_KEY=sk-...          # your key
python -m hello_agent.run "What is AgentsML?"
```

The generated smoke test, `python -c "import hello_agent.graph"`, creates the OpenAI client at import time, so it fails with `Missing credentials` unless `OPENAI_API_KEY` is set.

To check the run path without a real key, we pointed the project at a local stub server that returns a canned chat completion (`OPENAI_BASE_URL` is honoured). Observed output:

```text
Local stub reply: AgentsML is a portable agent spec.
```

## 7. Next steps

- **Add a tool and approvals.** Declare it under `tools:` with `input_schema`, `side_effect`, and `needs_approval`, then list it in an agent's `tools:`. See the [tutorial](tutorial-one-spec-many-frameworks.md).
- **Compile to another framework.** The same document compiles to `openai-agents`, `google-adk`, `crewai`, and `mastra`. The [tutorial](tutorial-one-spec-many-frameworks.md) shows each one's output.
- **Read more.** Draw the graph with `agentsml graph hello-agent.agentsml.yaml --format mermaid`. Spec chapters are in [`spec/`](https://github.com/indoos/agentsml/tree/main/spec), examples in [`examples/`](https://github.com/indoos/agentsml/tree/main/examples), and the live editor at [indoos.github.io/agentsml](https://indoos.github.io/agentsml/).
