# IAMDefender — Monthly Review Checklist

> **Why:** IAM is the #1 cloud breach vector. AI agents make it worse by generating over-permissioned roles.

## Monthly

- [ ] Run IAMDefender across all IaC repositories
  ```bash
  python3 iam-defender/scan.py --path . --detect-ai-patterns --format json
  ```
- [ ] Review newly generated IaC for over-permissioned roles
- [ ] Update AI-generated IaC patterns based on agent model updates
  - New Claude Code, Copilot, CodeGemini IaC generation patterns
- [ ] Check for new AWS/Azure/GCP managed policies
  - Update baseline least-privilege suggestions
- [ ] Verify least-privilege suggestions are practical
  - Test scoped-down policies against production workloads

## Quarterly

- [ ] Full audit of all production IAM roles vs IaC definitions
  - Drift detection between Terraform and actual AWS IAM
- [ ] Run privilege escalation path analysis
- [ ] Update Kubernetes RBAC rules for new API versions
- [ ] Review cross-account trust relationships
- [ ] Benchmark AI-generated IaC permission density
