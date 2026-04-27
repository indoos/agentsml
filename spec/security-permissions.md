# AgentsML Security And Permissions Draft

Status: draft v0.1 seed

## Principles

- Secrets are referenced, never embedded.
- Side effects are declared structurally.
- Human approvals are explicit workflow primitives.
- Remote agent, tool, API, browser, and payment boundaries are visible.
- Audit-relevant actions emit durable events.

## Side Effect Classes

- `read`
- `write`
- `delete`
- `browser`
- `external`
- `payment`
- `unknown`

Compilers should warn on `unknown` and require approval for risky classes unless policy says otherwise.

## Permission Shape

```yaml
permissions:
  side_effect: payment
  approval: required
  scopes:
    - checkout:create
  auth:
    secret_ref: commerce_oauth
```

## Trust Boundaries

AgentsML should model boundaries for:

- local code
- external API
- MCP server
- remote A2A agent
- browser/web automation
- payment/commerce
- human approval

## Audit

Audit events should include:

- actor
- action
- target
- timestamp
- input reference
- output reference
- approval reference
- trace/span reference

