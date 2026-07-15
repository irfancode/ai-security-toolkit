# IAMDefender — IaC IAM Permission Scanner for AI-Generated Roles

> *"AI agents frequently commit over-permissioned IAM roles faster than any human code reviewer can catch."* — Cycode Agent Risk Analysis 2026

**IAMDefender** scans Infrastructure-as-Code (Terraform, CloudFormation, Pulumi, and Kubernetes RBAC) for over-permissioned IAM roles, wildcard actions, privilege escalation paths, and AI-agent-specific anti-patterns in identity configurations.

## The Problem

- AI agents generate IaC with `"Action": "*"` and `"Resource": "*"` as default patterns
- Over-permissioned roles are the #1 cloud breach vector
- AI agents don't understand least-privilege — they copy examples with excessive permissions
- Manual IaC review at machine-speed is impossible

## Features

- **Wildcard Detection** — Flags `"Action": "*"`, `"Resource": "*"`, and broad `"Effect": "Allow"` blocks
- **Privilege Escalation Paths** — Detects IAM configurations that allow privilege escalation (PassRole, AssumeRole chains, policy attachment)
- **AI-Generated IaC Detection** — Identifies permission patterns characteristic of AI code generation (repetitive broad permissions, SDK-generated templates)
- **Least-Privilege Analysis** — Suggests scoped-down permissions for detected actions
- **Cross-Resource Trust** — Detects overly permissive trust policies
- **Kubernetes RBAC** — Scans ClusterRole, Role, ClusterRoleBinding for wildcards and escalation paths
- **Policy Diff** — Compares proposed changes against a baseline least-privilege policy
- **Remediation Mode** — Auto-generates scoped-down IAM policies

## Supported IaC Formats

| Format | Status |
|---|---|
| **Terraform** (`aws_iam_role`, `aws_iam_policy`, etc.) | Supported |
| **AWS CloudFormation** (`AWS::IAM::Role`, `AWS::IAM::Policy`) | Supported |
| **Pulumi** (TypeScript/Python/Go IAM resources) | Supported |
| **Kubernetes RBAC** (Role, ClusterRole, RoleBinding) | Supported |
| **AWS CDK** (iam.Role, iam.PolicyStatement) | Parsed via synthesized template |
| **Azure ARM / GCP IAM** | In Development |

## Quick Start

```bash
# Scan a Terraform directory
python3 iam-defender/scan.py --path terraform/environments/prod

# Scan with severity filtering
python3 iam-defender/scan.py --path terraform/ --threshold high --format json

# Generate least-privilege policy suggestion
python3 iam-defender/remediate.py --input tf-policy.json --output suggested-policy.json

# AI-generated IaC pattern scan
python3 iam-defender/scan.py --path . --detect-ai-patterns
```

## Example Output

```json
{
  "scan_id": "iam-20260715-001",
  "findings": [
    {
      "file": "terraform/main.tf:42",
      "resource": "aws_iam_role.api_gateway_role",
      "finding_type": "wildcard-action",
      "severity": "CRITICAL",
      "statement": "Action = [\"*\"] on Resource = \"*\"",
      "ai_generated": true,
      "remediation": "Replace Action = [\"*\"] with specific actions: apigateway:*, execute-api:Invoke",
      "least_privilege_suggestion": {
        "actions": ["apigateway:GET", "apigateway:POST", "execute-api:Invoke"],
        "resources": ["arn:aws:execute-api:us-east-1:123456789012:api-id/*"]
      }
    }
  ],
  "summary": {
    "total": 12,
    "critical": 3,
    "high": 5,
    "medium": 3,
    "low": 1,
    "ai_generated": 8
  }
}
```

## Common AI IaC Anti-Patterns Detected

| Pattern | Example | Risk |
|---|---|---|
| Action wildcard | `Action = ["*"]` | Full access |
| Resource wildcard | `Resource = ["*"]` | Data exposure |
| PassRole to untrusted | `iam:PassRole` with `Resource = "*"` | Privilege escalation |
| AssumeRole from all | `AWS: "*"` in AssumeRole policy | Cross-account abuse |
| Replicated admin role | Same permissions as `AdministratorAccess` | Over-privilege |
| All services access | `ec2:*`, `s3:*`, `lambda:*`, `iam:*` combined | Full cloud admin |
| No condition block | Missing `Condition` on sensitive actions | Unrestricted access |
| Hardcoded account ID | `arn:aws:iam::123456789012:role/*` without context | Staging leakage to prod |

## File Structure

```
iam-defender/
├── README.md
├── scan.py                # Core scanner
├── remediate.py           # Least-privilege suggestion engine
├── parsers/
│   ├── terraform.py       # Terraform IAM parser
│   ├── cloudformation.py  # CloudFormation IAM parser
│   ├── pulumi.py          # Pulumi IAM parser
│   └── k8s_rbac.py        # Kubernetes RBAC parser
├── rules/
│   ├── wildcard.py        # Wildcard detection rules
│   ├── escalation.py      # Privilege escalation path rules
│   ├── ai_patterns.py     # AI-generated IaC pattern detection
│   └── cross_account.py   # Cross-account trust analysis
├── action.yml
├── CHECKLIST.md
└── CONTRIBUTING.md
```

## CHECKLIST.md — Monthly Review

- [ ] Review all new IaC templates for over-permissioned roles
- [ ] Update AI-generated IaC patterns based on agent model updates
- [ ] Verify least-privilege suggestions are practical and not breaking
- [ ] Check for new AWS/Azure/GCP managed policies and update baselines
- [ ] Audit AI-generated IaC that bypassed detection in the last 30 days
- [ ] Review Kubernetes RBAC for wildcard Subjects
- [ ] Run baseline diff against production IAM policies
