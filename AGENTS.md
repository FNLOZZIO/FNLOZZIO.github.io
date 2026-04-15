# FNLOZZIO Public Pages AGENTS Policy

## Scope

- Own the public-only static site for legal notices and disclosures.
- Keep the repository safe for public publication.

## Deterministic Read Order

1. `README.md`
2. `AGENTS.md`

## Baseline Checks

- `make bootstrap`
- `make test`
- `make smoke`
- `make consistency`
- `make ci`

Run `make secret-scan` whenever public content changes touch auth, privacy, or integration-boundary wording.

## Execution Policy

- Keep the site static and public-only; no non-public implementation details belong here.
- Treat `Makefile` as the canonical execution surface for validation and CI.
- Update public pages and validation tooling together when the publication contract changes.

## Guardrails

- Do not publish secrets, tokens, hostnames, non-public IP addresses, or non-public architecture details.
- Do not introduce JavaScript frameworks, analytics, or third-party trackers without an explicit governance change.
- Prefer additive public pages over editing historical notices without keeping their intent auditable.

## Repo Operating Characteristics

- Agents may mutate:
  - public HTML/CSS pages, public legal/privacy docs, and bounded validation tooling
- Agents must not mutate:
  - non-public implementation details, runtime configuration, or unpublished credentials
- Primary outputs and handoffs:
  - public GitHub Pages content
  - repo-local documentation and validation logic
  - legal/privacy notices
