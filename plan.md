# Lambdalith Cleanup Plan

## Remaining Work / Open Questions

1. Implement some admin forms to be ssr rendered by jinja2 templates (e.g. user management, password reset request form); these can be very basic and unstyled, but should demonstrate the ability to render HTML from Lambda and handle form submissions.
2. Decide where API keys live (hardcoded in `app.config` now). Move to env/Secrets Manager or document as a local-only placeholder.
3. Add minimal tests (auth register/login/logout + health) or explicitly mark tests as out-of-scope for now.
4. Implement login-attempts rate limiting (table exists but no logic uses it yet).
5. Either populate `ruff.toml` with actual lint/format rules or remove the empty file.

## Not Now
- Add SES permissions to `template.yaml` (password reset uses `ses:SendEmail`) or stub/disable email sending for now.

## Rules

- **No new dependencies.** Every solution must use packages already in `requirements.txt` or the README Dependencies section. Do not introduce new libraries, CDK alpha modules, or third-party tools. If a feature can't be done with what's already available, find another way or skip it.

No fake events. No manual `json.loads(event['body'])`. No `response()` helper dicts.
