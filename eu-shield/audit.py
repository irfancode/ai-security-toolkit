#!/usr/bin/env python3
import argparse
import json
import sys
from datetime import datetime, date

DEADLINE = date(2026, 8, 2)


REQUIREMENTS = {
    "risk_classification": {
        "name": "Risk Classification (Art. 6-7)",
        "checks": [
            {"id": "RC-1", "description": "AI system classified as minimal/low/high/unacceptable risk", "weight": 10},
            {"id": "RC-2", "description": "High-risk classification criteria documented", "weight": 5},
            {"id": "RC-3", "description": "Unacceptable risk systems not deployed", "weight": 15},
        ]
    },
    "data_governance": {
        "name": "Data Governance (Art. 10)",
        "checks": [
            {"id": "DG-1", "description": "Training data provenance documented", "weight": 10},
            {"id": "DG-2", "description": "Bias testing performed and documented", "weight": 8},
            {"id": "DG-3", "description": "Data minimization applied", "weight": 5},
            {"id": "DG-4", "description": "PII scrubbing verified", "weight": 8},
            {"id": "DG-5", "description": "Data lineage end-to-end documented", "weight": 6},
        ]
    },
    "documentation": {
        "name": "Technical Documentation (Art. 11)",
        "checks": [
            {"id": "TD-1", "description": "Model card / system description exists", "weight": 8},
            {"id": "TD-2", "description": "Intended purpose and limitations documented", "weight": 6},
            {"id": "TD-3", "description": "Version history maintained", "weight": 4},
            {"id": "TD-4", "description": "Risk mitigation measures documented", "weight": 7},
        ]
    },
    "transparency": {
        "name": "Transparency (Art. 13, 50)",
        "checks": [
            {"id": "TR-1", "description": "Users informed they are interacting with AI", "weight": 8},
            {"id": "TR-2", "description": "AI-generated content labeled/marked", "weight": 7},
            {"id": "TR-3", "description": "Capabilities and limitations disclosed", "weight": 5},
        ]
    },
    "human_oversight": {
        "name": "Human Oversight (Art. 14)",
        "checks": [
            {"id": "HO-1", "description": "Human-in-the-loop mechanism implemented", "weight": 9},
            {"id": "HO-2", "description": "Override/stop capability documented", "weight": 8},
            {"id": "HO-3", "description": "Human operator training program exists", "weight": 5},
            {"id": "HO-4", "description": "Escalation procedure documented", "weight": 6},
        ]
    },
    "accuracy_robustness": {
        "name": "Accuracy & Robustness (Art. 15)",
        "checks": [
            {"id": "AR-1", "description": "Accuracy benchmarks defined and measured", "weight": 7},
            {"id": "AR-2", "description": "Error rate documented", "weight": 5},
            {"id": "AR-3", "description": "Robustness to adversarial inputs tested", "weight": 6},
            {"id": "AR-4", "description": "Reproducibility conditions documented", "weight": 4},
        ]
    },
    "conformity": {
        "name": "Conformity Assessment (Art. 48)",
        "checks": [
            {"id": "CA-1", "description": "EU declaration of conformity drafted", "weight": 8},
            {"id": "CA-2", "description": "Notified body engaged (if required)", "weight": 10},
            {"id": "CA-3", "description": "CE marking applied", "weight": 6},
        ]
    },
    "incident_reporting": {
        "name": "Incident Reporting (Art. 73)",
        "checks": [
            {"id": "IR-1", "description": "Serious incident reporting mechanism documented", "weight": 8},
            {"id": "IR-2", "description": "15-day reporting timeline procedures in place", "weight": 7},
            {"id": "IR-3", "description": "Incident log maintained", "weight": 5},
        ]
    },
    "gpai": {
        "name": "GPAI Requirements (Art. 55-56)",
        "checks": [
            {"id": "GP-1", "description": "Training data summary published", "weight": 6},
            {"id": "GP-2", "description": "Copyright policy documented", "weight": 5},
            {"id": "GP-3", "description": "Energy consumption recorded", "weight": 4},
        ]
    }
}


def classify_risk(manifest: dict) -> str:
    if manifest.get("risk_classification") in ("high", "limited", "minimal", "unacceptable"):
        return manifest["risk_classification"]
    intended = (manifest.get("intended_use") or "").lower()
    if any(kw in intended for kw in ["recruitment", "credit", "law enforcement", "migration", "education", "biometric"]):
        return "high"
    if "critical infrastructure" in intended:
        return "high"
    if manifest.get("provider") in ("openai", "anthropic", "google", "meta") or "general" in intended:
        return "limited"
    return "minimal"


def audit(manifest: dict) -> dict:
    results = []
    total_weight = 0
    passed_weight = 0

    risk = classify_risk(manifest)
    days_left = (DEADLINE - date.today()).days

    for req_key, req_def in REQUIREMENTS.items():
        category_results = []
        for check in req_def["checks"]:
            status = "fail"
            evidence = ""
            cid = check["id"]
            desc = check["description"]

            manifest_checks = manifest.get("_checks", {})
            if cid in manifest_checks:
                status = manifest_checks[cid].get("status", "fail")
                evidence = manifest_checks[cid].get("evidence", "")
            else:
                evidence = infer_evidence(cid, manifest)

            total_weight += check["weight"]
            if status == "pass":
                passed_weight += check["weight"]
            elif status == "partial":
                passed_weight += check["weight"] * 0.5

            category_results.append({
                "id": cid,
                "check": desc,
                "status": status,
                "evidence": evidence,
            })

        passed_count = sum(1 for c in category_results if c["status"] == "pass")
        partial_count = sum(1 for c in category_results if c["status"] == "partial")
        fail_count = sum(1 for c in category_results if c["status"] == "fail")
        results.append({
            "category": req_def["name"],
            "checks": category_results,
            "summary": f"{passed_count} pass, {partial_count} partial, {fail_count} fail",
        })

    compliance_pct = round((passed_weight / total_weight * 100) if total_weight > 0 else 0, 1)
    passed_categories = sum(1 for r in results if all(c["status"] == "pass" for c in r["checks"]))
    failed_categories = [r for r in results if any(c["status"] == "fail" for c in r["checks"])]

    return {
        "model": manifest.get("model_name", "unknown"),
        "version": manifest.get("version", "unknown"),
        "risk_classification": risk,
        "audit_date": date.today().isoformat(),
        "eu_aiact_deadline": DEADLINE.isoformat(),
        "days_remaining": max(0, days_left),
        "compliance_score": compliance_pct,
        "compliant": compliance_pct >= 80,
        "categories": results,
        "failed_categories": [r["category"] for r in failed_categories],
        "gaps": [
            f"{r['category']}: {c['check']}"
            for r in failed_categories
            for c in r["checks"] if c["status"] == "fail"
        ],
        "potential_fine_risk": "HIGH" if compliance_pct < 50 else ("MEDIUM" if compliance_pct < 80 else "LOW"),
    }


def infer_evidence(cid: str, manifest: dict) -> str:
    if cid == "RC-1":
        return f"Classified as {manifest.get('risk_classification', 'not specified')}"
    if cid == "DG-1":
        sources = manifest.get("data_sources", [])
        return f"{len(sources)} data sources documented" if sources else "No data sources documented"
    if cid == "DG-4":
        for s in manifest.get("data_sources", []):
            if s.get("pii_scrubbed"):
                return "PII scrubbing confirmed on at least one source"
        return "No PII scrubbing evidence"
    if cid == "TR-1":
        tr = manifest.get("transparency", {})
        return f"AI disclosure: {tr.get('ai_disclosure', False)}"
    if cid == "HO-1":
        ho = manifest.get("human_oversight", {})
        return f"Mechanism: {ho.get('mechanism', 'not documented')}"
    if cid == "GP-3":
        tr = manifest.get("training", {})
        return f"Energy: {tr.get('energy_consumption_kwh', 'not recorded')} kWh"
    return "No evidence provided (check not explicitly evaluated)"


def format_html(report: dict) -> str:
    risk_color = {"high": "red", "limited": "orange", "minimal": "green", "unacceptable": "darkred"}
    color = risk_color.get(report["risk_classification"], "gray")

    rows = ""
    for cat in report["categories"]:
        status_color = "green" if all(c["status"] == "pass" for c in cat["checks"]) else "red"
        rows += f"<tr><td>{cat['category']}</td><td style='color:{status_color}'>{cat['summary']}</td></tr>"

    gaps = "".join(f"<li>{g}</li>" for g in report.get("gaps", []))

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>EU AI Act Compliance — {report['model']}</title>
<style>body{{font-family:sans-serif;max-width:900px;margin:40px auto;padding:0 20px;line-height:1.6}}
h1{{border-bottom:2px solid #333;padding-bottom:10px}}
.metric{{display:inline-block;margin:10px;padding:15px;border-radius:8px;color:white;text-align:center}}
.metric h2{{margin:0;font-size:2em}} .metric p{{margin:5px 0 0;font-size:0.9em}}
.critical{{background:#dc3545}} .medium{{background:#ffc107;color:#333}} .low{{background:#28a745}}
table{{width:100%;border-collapse:collapse;margin:20px 0}}
th,td{{text-align:left;padding:10px;border-bottom:1px solid #ddd}}
.fail{{color:#dc3545;font-weight:bold}} .urgent{{background:#fff3cd;padding:15px;border-radius:8px;border-left:4px solid #ffc107}}
</style></head><body>
<h1>EU AI Act Compliance Report</h1>
<p><strong>Model:</strong> {report['model']} v{report['version']}</p>
<p><strong>Risk Classification:</strong> <span style="color:{color};font-weight:bold">{report['risk_classification'].upper()}</span></p>
<p><strong>Audit Date:</strong> {report['audit_date']}</p>

<div class="metric {'critical' if report['compliance_score']<50 else 'medium' if report['compliance_score']<80 else 'low'}">
  <h2>{report['compliance_score']}%</h2><p>Compliance Score</p></div>
<div class="metric {'critical' if report['days_remaining']<30 else 'medium' if report['days_remaining']<90 else 'low'}">
  <h2>{report['days_remaining']} days</h2><p>Until Deadline</p></div>
<div class="metric {'critical' if report.get('potential_fine_risk')=='HIGH' else 'medium'}">
  <h2>{report.get('potential_fine_risk','UNKNOWN')}</h2><p>Fine Risk</p></div>

<h2>Category Results</h2>
<table><tr><th>Category</th><th>Status</th></tr>{rows}</table>

<h2>Gaps Identified</h2>
{"<ol>" + gaps + "</ol>" if gaps else "<p>No critical gaps identified.</p>"}

<div class="urgent">
<strong>⚠ Deadline Reminder:</strong> {report['days_remaining']} days until August 2, 2026.<br>
Potential fines: up to 7% of global annual turnover or €35M.
</div>
</body></html>"""


def main():
    parser = argparse.ArgumentParser("EUShield — EU AI Act compliance auditor")
    parser.add_argument("--manifest", required=True, help="Model manifest JSON file")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--format", choices=["json", "html", "text"], default="json")
    parser.add_argument("--gap-only", action="store_true", help="Only show gaps")
    parser.add_argument("--ci-gate", action="store_true", help="Exit non-zero on failures")
    parser.add_argument("--fail-on", default="high-severity-gaps", choices=["any-gap", "high-severity-gaps", "none"])
    args = parser.parse_args()

    with open(args.manifest) as f:
        manifest = json.load(f)

    report = audit(manifest)

    if args.gap_only:
        output = json.dumps({"gaps": report["gaps"], "count": len(report["gaps"])}, indent=2)
    elif args.format == "html":
        output = format_html(report)
    elif args.format == "json":
        output = json.dumps(report, indent=2)
    else:
        lines = [
            f"EUShield — EU AI Act Compliance Report",
            f"Model: {report['model']} v{report['version']}",
            f"Risk: {report['risk_classification'].upper()}",
            f"Compliance: {report['compliance_score']}%",
            f"Days to deadline: {report['days_remaining']}",
            f"Fine risk: {report['potential_fine_risk']}",
            "",
            "Gaps:",
        ]
        for g in report.get("gaps", []):
            lines.append(f"  ❌ {g}")
        output = "\n".join(lines)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Report written to {args.output}")
    else:
        print(output)

    if args.ci_gate:
        if args.fail_on == "any-gap" and report.get("gaps"):
            sys.exit(1)
        elif args.fail_on == "high-severity-gaps" and report["compliance_score"] < 50:
            sys.exit(1)


if __name__ == "__main__":
    main()
