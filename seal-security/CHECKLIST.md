# SealSecurity — Monthly Review Checklist

> **Why:** AI agents evolve rapidly. New tools emerge with new coding patterns. This checklist ensures your secrets defense stays ahead.

## Monthly (First Monday)

- [ ] Update `patterns/agent.json` with new AI agent credential patterns
  - Check release notes for Claude Code, Copilot, CodeGemini, Cursor
  - Review Cycode, GitGuardian, and Check Point threat reports
  - Add any new API key formats from cloud providers
- [ ] Review false positives from the last 30 days
  - Update `.sealpatterns.json` or add `seal-skip-line` annotations
  - Consider removing overbroad patterns that cause too many FPs
- [ ] Verify pre-commit hook is installed on all developer machines
  - Check `.git/hooks/pre-commit` exists and contains seal-security

## Quarterly

- [ ] Run seal-security across the entire git history
  ```bash
  seal-security scan --path . --format json --output historical-scan.json
  ```
- [ ] Audit bypassed commits (secrets that made it past pre-commit but were caught in CI)
  - Review commit messages and authors to identify patterns
- [ ] Check for new cloud provider credential formats
  - AWS: new STS formats, service-specific keys
  - Azure: managed identity tokens, federated credentials
  - GCP: workload identity federation keys
- [ ] Update severity scoring based on real-world incident data
- [ ] Review AI-generated code commits for secret injection patterns
