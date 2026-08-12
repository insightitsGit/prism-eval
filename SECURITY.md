# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.2.x   | Yes — security fixes |
| < 0.2   | No |

Prism-Eval is an **open-source pre-deploy evaluation tool**. It is not a runtime enforcement gateway. For production interception of poisoned tool arguments, use [Prism-Shield](https://pypi.org/project/prism-shield/) (or equivalent) in addition to this library.

## Reporting a vulnerability

Please **do not** open a public GitHub issue for security vulnerabilities.

Preferred (private):

1. [GitHub Security Advisory (private vulnerability reporting)](https://github.com/insightitsGit/prism-eval/security/advisories/new)  
2. Email: **security@insightits.com**

Include:

1. Affected version / commit SHA  
2. Reproduction steps (minimal corpus + agent stub if possible)  
3. Impact assessment (false accept, CI bypass, supply-chain, etc.)  
4. Any suggested fix  

We aim to acknowledge within **3 business days** and provide a remediation plan within **14 days** for confirmed critical issues.

## Public repository protections

This repo enables:

- Secret scanning + push protection  
- Dependabot alerts and security updates  
- Private vulnerability reporting  
- Branch protection on `main` (no force-push / no branch deletion; CI required for PRs)  
- Issue templates that route security away from public issues  

Do not commit tokens, `.env` files, or PyPI / cloud credentials. Use GitHub Actions secrets only.

## Scope

### In scope
- False-accept bugs in the security oracle (poisoned values scored as PASS)
- Path traversal / unsafe corpus loading
- Supply-chain issues in release artifacts
- Secrets leakage via CLI/report exporters

### Out of scope
- Agents under test returning wrong values (that is what the suite detects)
- Third-party model providers
- Social engineering against maintainers

## Threat model

See [`docs/THREAT_MODEL.md`](docs/THREAT_MODEL.md).

## Safe defaults

- Suite FAIL when `critical_false_accept_count > 0` (`g4_invariant_held == false`)
- Per-case timeouts and bounded concurrency
- Schema contract hashing over field names/types (not values)
- Audit receipts written only to paths you specify

## Disclosure policy

We follow coordinated disclosure. Fixes ship in a patch release with a CHANGELOG entry under **Security**.
