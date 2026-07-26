# Security Policy

## Supported Versions

This project does not publish versioned releases yet. Security fixes target the
current `main` branch.

| Version | Supported |
| --- | --- |
| `main` | Yes |
| Older commits and forks | No guaranteed support |

## Report A Vulnerability

Do not disclose a vulnerability, credential, private widget value, deployment
address, or reproduction containing sensitive data in a public issue.

Use GitHub's private
[Report a vulnerability](https://github.com/Ethereal49/ai-desk-card-online/security/advisories/new)
form. Include:

- the affected commit or file;
- the security impact and realistic attack path;
- minimal reproduction steps using synthetic data;
- any suggested mitigation;
- whether you believe the issue is already public.

The maintainer will review the report and coordinate next steps through the
private advisory. This project does not promise a fixed response or remediation
SLA.

## Security Boundaries

- The static browser is not an authorization boundary. Private deployments
  require HTTPS and server-side access control.
- `widgets.json` must contain only bounded display fields. Credentials, tokens,
  source IDs, paths, transcripts, prompts, responses, links, attendees, and
  private notes are forbidden.
- Source integrations are read-only. The repository does not authorize writes
  to Linear, Calendar, Codex, or other source systems.
- Deployment examples contain no real password, Basic Auth hash, private key,
  certificate lineage, or server-generated artifact.
- CI is deterministic, read-only, and does not receive deployment secrets.

Operational deployment questions that do not expose sensitive details may use
a normal issue. For setup guidance, see the
[deployment security boundary](deploy/README.md).
