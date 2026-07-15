#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import List, Dict


AI_PATTERNS = [
    {"name": "repetitive-wildcard", "pattern": r'("\*"[\s,]*){3,}', "desc": "Three or more wildcard entries suggest AI template copying"},
    {"name": "all-services-every-resource", "pattern": r'["\'](?:Action|actions)["\']\s*[:=]\s*\[?["\'].*["\']\s*\]?\s*\n\s*["\'](?:Resource|resources)["\']\s*[:=]\s*["\'][*]["\']', "desc": "Broad actions combined with resource wildcard"},
    {"name": "sdk-default-pattern", "pattern": r'["\'](?:sid|statement_id)["\']\s*[:=]\s*["\']VisualEditor\d+["\']', "desc": "SDK-generated statement ID suggests copy-paste IaC"},
    {"name": "no-condition-no-notresource", "pattern": r'(?s)Allow[^}]*?Action[^}]*?Resource[^}]*?\}[^}]*?\}(?!.*Condition)', "desc": "Allow block without Condition or NotResource"},
]


WILDCARD_RULES = [
    {"name": "action-wildcard", "severity": "CRITICAL", "check": lambda s: '"*"' in str(s.get("Action", s.get("actions", "")))},
    {"name": "resource-wildcard", "severity": "CRITICAL", "check": lambda s: '"*"' in str(s.get("Resource", s.get("resources", "")))},
    {"name": "principal-wildcard", "severity": "HIGH", "check": lambda s: '"*"' in str(s.get("Principal", s.get("principal", "")))},
]


ESCALATION_RULES = [
    {"name": "pass-role-wildcard", "severity": "CRITICAL", "check": lambda s: "iam:PassRole" in str(s.get("Action", [])) and '"*"' in str(s.get("Resource", []))},
    {"name": "assume-role-wildcard", "severity": "HIGH", "check": lambda s: "sts:AssumeRole" in str(s.get("Action", [])) and '"*"' in str(s.get("Principal", {}, ""))},
    {"name": "iam-full-access", "severity": "CRITICAL", "check": lambda s: "iam:*" in str(s.get("Action", []))},
]


class IAMFinding:
    def __init__(self, file_path, line, resource, finding_type, severity, statement, ai_generated, remediation):
        self.file_path = file_path
        self.line = line
        self.resource = resource
        self.finding_type = finding_type
        self.severity = severity
        self.statement = statement
        self.ai_generated = ai_generated
        self.remediation = remediation

    def to_dict(self):
        return {
            "file": f"{self.file_path}:{self.line}",
            "resource": self.resource,
            "finding_type": self.finding_type,
            "severity": self.severity,
            "statement": self.statement[:200],
            "ai_generated": self.ai_generated,
            "remediation": self.remediation,
        }


def extract_terraform_blocks(content: str) -> List[Dict]:
    blocks = []
    pattern = re.compile(r'resource\s+"aws_iam_(\w+)"\s+"([^"]+)"\s*{([^}]*)}', re.DOTALL)
    for match in pattern.finditer(content):
        blocks.append({
            "type": match.group(1),
            "name": match.group(2),
            "body": match.group(3).strip(),
            "start": content[:match.start()].count("\n") + 1,
        })

    policy_pattern = re.compile(r'resource\s+"aws_iam_policy"\s+"([^"]+)"\s*{([^}]*)}', re.DOTALL)
    for match in policy_pattern.finditer(content):
        blocks.append({
            "type": "policy",
            "name": match.group(1),
            "body": match.group(2).strip(),
            "start": content[:match.start()].count("\n") + 1,
        })
    return blocks


def extract_statements_from_body(body: str) -> List[Dict]:
    statements = []
    stmt_pattern = re.compile(r'(statement|policy)\s*{([^}]*)}', re.DOTALL)
    for match in stmt_pattern.finditer(body):
        raw = match.group(2)
        statements.append({
            "raw": raw,
            "has_action_all": '"*"' in extract_quoted_list(raw, "Action"),
            "has_resource_all": '"*"' in extract_quoted_list(raw, "Resource"),
            "has_principal_all": '"*"' in extract_quoted_list(raw, "Principal"),
        })
    return statements


def extract_quoted_list(text: str, key: str) -> List[str]:
    pattern = re.compile(rf'"{key}"\s*=\s*\[([^\]]*)\]', re.IGNORECASE)
    match = pattern.search(text)
    if match:
        return re.findall(r'"([^"]+)"', match.group(1))
    single = re.compile(rf'"{key}"\s*=\s*"([^"]+)"', re.IGNORECASE)
    m = single.search(text)
    if m:
        return [m.group(1)]
    return []


def detect_ai_iaa(content: str) -> List[Dict]:
    findings = []
    for pat in AI_PATTERNS:
        for match in re.finditer(pat["pattern"], content, re.DOTALL | re.MULTILINE):
            line = content[:match.start()].count("\n") + 1
            findings.append({
                "line": line,
                "pattern": pat["name"],
                "description": pat["desc"],
            })
    return findings


def scan_terraform(path: str, threshold: str, detect_ai: bool) -> List[IAMFinding]:
    findings = []
    path = Path(path)
    files = list(path.rglob("*.tf")) + list(path.rglob("*.tf.json"))
    severity_order = {"low": 0, "medium": 1, "high": 2, "critical": 3}
    min_sev = severity_order.get(threshold, 0)

    for fpath in files:
        with open(fpath) as f:
            content = f.read()

        blocks = extract_terraform_blocks(content)
        for block in blocks:
            statements = extract_statements_from_body(block["body"])
            for stmt in statements:
                for rule in WILDCARD_RULES + ESCALATION_RULES:
                    if rule["check"](stmt) and severity_order.get(rule["severity"].lower(), 0) >= min_sev:
                        ai_flag = bool(detect_ai and re.search(r'["\']\*["\']', str(stmt.get("raw", ""))))
                        remediation = f"Review and scope {rule['name']} to specific resources/actions"
                        findings.append(IAMFinding(
                            file_path=str(fpath),
                            line=block["start"],
                            resource=f"aws_iam_{block['type']}.{block['name']}",
                            finding_type=rule["name"],
                            severity=rule["severity"],
                            statement=f"Action or Resource uses wildcard in {block['type']}.{block['name']}",
                            ai_generated=ai_flag,
                            remediation=remediation,
                        ))

        if detect_ai:
            ai_matches = detect_ai_iaa(content)
            for m in ai_matches:
                findings.append(IAMFinding(
                    file_path=str(fpath),
                    line=m["line"],
                    resource="(file-level)",
                    finding_type=f"ai-pattern-{m['pattern']}",
                    severity="medium",
                    statement=m["description"],
                    ai_generated=True,
                    remediation="Review AI-generated IAM patterns for over-permissioning",
                ))

    return findings


def main():
    parser = argparse.ArgumentParser("IAMDefender — IaC IAM permission scanner")
    parser.add_argument("--path", required=True, help="Path to IaC directory")
    parser.add_argument("--threshold", default="medium", choices=["low", "medium", "high", "critical"])
    parser.add_argument("--format", default="text", choices=["text", "json"])
    parser.add_argument("--detect-ai-patterns", action="store_true", help="Detect AI-generated IaC patterns")
    parser.add_argument("--output", help="Output file path")

    args = parser.parse_args()

    findings = scan_terraform(args.path, args.threshold, args.detect_ai_patterns)

    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    findings.sort(key=lambda f: severity_order.get(f.severity.lower(), 99))

    summary = {"critical": 0, "high": 0, "medium": 0, "low": 0, "ai_generated": 0}
    for f in findings:
        summary[f.severity.lower()] = summary.get(f.severity.lower(), 0) + 1
        if f.ai_generated:
            summary["ai_generated"] += 1

    if args.format == "json":
        output = json.dumps({
            "scan_id": f"iam-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
            "findings": [f.to_dict() for f in findings],
            "summary": summary,
        }, indent=2)
    else:
        lines = [f"IAMDefender — {len(findings)} findings", ""]
        if not findings:
            lines.append("No IAM issues found.")
        else:
            for f in findings:
                flag = "🤖" if f.ai_generated else "  "
                lines.append(f"  [{f.severity.upper():8}] {flag} {f.file_path}:{f.line}")
                lines.append(f"           {f.resource} — {f.finding_type}")
                lines.append(f"           {f.remediation}")
                lines.append("")
        lines.append(f"Summary: {summary['critical']} critical, {summary['high']} high, {summary['medium']} medium, {summary['low']} low")
        lines.append(f"AI-generated patterns: {summary['ai_generated']}")
        output = "\n".join(lines)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Results written to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    from datetime import datetime
    main()
