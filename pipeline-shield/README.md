# PipelineShield — Inline Agentic Remediation for CI/CD

> *"Traditional SAST tools flag bugs but cause 7-hour weekly delays. Transition to Inline Agentic Remediation where AI security agents auto-triage and patch code in the pipeline."* — SANS 2026 AI Survey

**PipelineShield** is a GitHub Action (and generic CI plugin) that catches security findings from SAST, SCA, and secret scanners and **auto-remediates them inline** — filing PRs with patches rather than just opening tickets.

## The Problem

| Issue | Impact |
|---|---|
| SAST tools block pipelines for days | 7h/week developer delay per team |
| Security teams drown in findings | 45% of AI-generated code is vulnerable |
| Fixes require human context-switching | Critical vulnerabilities sit unpatched for weeks |
| AI agents generate same bugs repeatedly | No feedback loop to the agent |

## How It Works

1. Your CI runs SAST/SCA tools (Semgrep, CodeQL, Trivy, Snyk, etc.)
2. PipelineShield parses the results (SARIF, JSON) and **auto-triages** each finding
3. For findings with known fix patterns, PipelineShield **generates a patch** and files a PR
4. For ambiguous findings, it creates a **triage report** with severity classification
5. Results feed back into a **blocklist** that prevents the same pattern from recurring

## Quick Start

```yaml
# .github/workflows/pipeline-shield.yml
name: PipelineShield
on:
  pull_request:
    branches: [main]
jobs:
  shield:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
      security-events: write
    steps:
      - uses: actions/checkout@v4

      # Run your existing SAST tool
      - name: Semgrep
        uses: semgrep/semgrep-action@v1
        continue-on-error: true

      # PipelineShield auto-remediates findings
      - name: PipelineShield Remediate
        uses: ./pipeline-shield/action
        with:
          input-file: results.sarif
          auto-fix: true
          create-pr: true
          severity-threshold: high
          block-threshold: critical
```

## Configuration

```yaml
# pipeline-shield.yml
remediation:
  auto_fix: true
  create_pr: true
  pr_label: "security:auto-remediation"
  severity_threshold: "high"   # auto-fix high and above
  block_threshold: "critical"  # block pipeline on critical

triage:
  categories:
    - type: "sql-injection"
      strategy: "parameterize-query"
    - type: "hardcoded-secret"
      strategy: "migrate-to-vault"
    - type: "xss"
      strategy: "add-output-encoding"
    - type: "iam-wildcard"
      strategy: "restrict-iam-action"

blocklist:
  enabled: true
  storage: "github-issues"  # or "s3" or "local"
```

## Supported Tools

- **SAST:** Semgrep, CodeQL, SonarQube, Snyk Code
- **SCA:** Trivy, Dependabot, Snyk OpenSource, OWASP DC
- **Secrets:** SealSecurity, GitLeaks, TruffleHog
- **IaC:** Checkov, Terrascan, tfsec

## File Structure

```
pipeline-shield/
├── README.md
├── action.yml
├── Dockerfile
├── shield.py              # Core engine
├── remediators/
│   ├── sql.py             # SQL injection fixer
│   ├── secrets.py         # Secret migration fixer
│   ├── xss.py             # XSS output encoding fixer
│   ├── iam.py             # IAM policy restrictor
│   └── sast_generic.py    # Generic SAST finding pattern fixer
├── parsers/
│   ├── sarif.py           # SARIF parser
│   ├── semgrep.py         # Semgrep JSON parser
│   └── trivy.py           # Trivy JSON parser
├── CHECKLIST.md
└── CONTRIBUTING.md
```

## CHECKLIST.md — Monthly Review

- [ ] Review auto-remediation false positives from the last 30 days
- [ ] Analyze AI-generated code patterns that bypass current rules
- [ ] Update `remediators/` with fix patterns for new vulnerability classes
- [ ] Verify blocked findings are actually remediated (not just re-opened)
- [ ] Check blocklist for repeated failures — flag for agent training
- [ ] Rotate any secrets that were caught but made it past a previous scan
- [ ] Review SAST/SCA tool configs for coverage gaps against AI-generated code
