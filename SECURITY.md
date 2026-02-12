# Security Policy

## Reporting a Vulnerability

Please do not report security vulnerabilities in public issues.

To report a vulnerability, email: `ashley.maher@didymodesigns.com.au`

Include:
- Affected version/commit
- Reproduction steps or proof of concept
- Potential impact
- Suggested remediation (if known)

We will acknowledge receipt as soon as possible and coordinate a fix and disclosure timeline.

## Scope

This repository processes medical data and potentially identifiable information (PII).
Security defects that could expose patient data, credentials, backups, or system access are in scope.

## Expectations for Changes

- Run `./tools/quality-gate.sh` before considering changes complete.
- Avoid logging PII or secrets.
- Keep dependencies updated and address known vulnerabilities promptly.
- Prefer least-privilege defaults and secure configuration.

