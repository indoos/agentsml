# AgentsML Diagnostics Draft

Status: draft v0.1 seed

Diagnostics make portability honest.

## Severity

- `info`
- `warning`
- `error`
- `fatal`

## Diagnostic Codes

- `unsupported_profile`
- `unsupported_feature`
- `lossy_mapping`
- `requires_adapter`
- `requires_target_extension`
- `missing_auth_binding`
- `missing_policy`
- `missing_schema`
- `ambiguous_reference`
- `unsafe_side_effect`
- `nonportable_expression`
- `target_version_unknown`

## Diagnostic Shape

```yaml
code: lossy_mapping
severity: warning
message: Target does not support arbitrary graph cycles.
path: workflows.main.edges[3]
target: dify
recommendation: Use agentsml-graph target extension or rewrite as bounded loop.
```

## Rules

- Compilers must emit `error` or `fatal` for unsupported required profiles.
- Compilers should emit `warning` for approximate mappings.
- Compilers must not silently remove approval gates, policies, auth requirements, or side-effect classifications.
- Diagnostics should include a path into the AgentsML document whenever possible.

