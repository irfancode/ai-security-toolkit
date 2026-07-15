# EUShield — EU AI Act Compliance Auditor

> *"The EU AI Act's strict compliance mandates for high-risk AI deployments kick in on August 2, 2026. Organizations must lock down data provenance, code pipelines, and model transparency immediately."* — Regulatory Alert 2026

**EUShield** audits your AI systems against the EU AI Act requirements — risk classification, data provenance, model transparency, human oversight, and documentation. It generates compliance reports, gap analyses, and remediation roadmaps.

## The Regulatory Deadline

| Milestone | Date | Requirement |
|---|---|---|
| **High-Risk AI compliance** | **Aug 2, 2026** | Full compliance for high-risk AI systems |
| GPAI code of practice | May 2026 | Transparency templates for general-purpose AI |
| National authority enforcement | Aug 2025 | Member state supervisory bodies operational |
| Fines up to | 7% global turnover | Or €35M, whichever is higher |

## What It Checks

| EU AI Act Requirement | EUShield Check | Status |
|---|---|---|
| **Risk Classification** | Classifies AI system as minimal/low/high/unacceptable risk | ✅ |
| **Data Governance** | Verifies data provenance, bias testing, training data documentation | ✅ |
| **Technical Documentation** | Generates required technical docs (Art. 11) | ✅ |
| **Transparency** | Checks disclosure requirements for AI-generated content | ✅ |
| **Human Oversight** | Verifies human-in-the-loop controls | ✅ |
| **Accuracy/Robustness** | Checks accuracy benchmarks, error rate documentation | ✅ |
| **Conformity Assessment** | Generates EU declaration of conformity (Art. 48) | ✅ |
| **Incident Reporting** | Serious incident reporting mechanism check | ✅ |
| **GPAI Requirements** | For general-purpose AI: training data summary, copyright policy | ✅ |

## Quick Start

```bash
# Audit a model manifest
python3 eu-shield/audit.py --manifest model-manifest.json

# Generate full compliance report
python3 eu-shield/audit.py --manifest model-manifest.json \
  --output eu-aiact-report.html \
  --format html

# Gap analysis only
python3 eu-shield/audit.py --manifest model-manifest.json \
  --gap-only \
  --output gap-analysis.json

# Continuous monitoring (CI/CD gate)
python3 eu-shield/audit.py --manifest model-manifest.json \
  --ci-gate \
  --fail-on high-severity-gaps
```

## Model Manifest Format

```json
{
  "model_name": "llm-v2-production",
  "version": "2.3.1",
  "provider": "azure-openai",
  "deployment_date": "2026-06-01",
  "risk_classification": "high",
  "intended_use": "Customer-facing code generation assistant",
  "data_sources": [
    {"name": "code-corpus-v3", "provenance": "internal-scm", "license": "proprietary"},
    {"name": "fine-tune-logs", "provenance": "production-telemetry", "pii_scrubbed": true}
  ],
  "training": {
    "completion_date": "2026-05-15",
    "compute_used": "1000 GPU-hours",
    "energy_consumption_kwh": 5000,
    "evaluation_accuracy": 0.94,
    "bias_testing": {"performed": true, "report_url": "https://.../bias-report.pdf"}
  },
  "human_oversight": {
    "mechanism": "human-in-the-loop",
    "escalation_procedure": "All code outputs reviewed before deployment"
  },
  "transparency": {
    "ai_disclosure": true,
    "labeling": "Generated with AI"
  }
}
```

## Example Compliance Report Summary

```
╔══════════════════════════════════════════════════════════╗
║  EU AI Act Compliance Report — llm-v2-production v2.3.1 ║
╠══════════════════════════════════════════════════════════╣
║  Risk Classification: HIGH (Article 6)                   ║
║  Overall Compliance: 73% — 6 pass, 2 fail, 4 partial    ║
╠══════════════════════════════════════════════════════════╣
║  FAIL: Data Provenance — Training data sources lack      ║
║  complete lineage documentation (Art. 10)                ║
║                                                          ║
║  FAIL: Incident Reporting — No documented mechanism for  ║
║  serious incident notification to supervisory authority  ║
║  within 15 days (Art. 73)                                ║
║                                                          ║
║  PARTIAL: Technical Documentation — Missing model card   ║
║  details on known limitations and edge cases (Art. 11)   ║
╠══════════════════════════════════════════════════════════╣
║  ⏰ 17 days until Aug 2, 2026 deadline                   ║
║  Potential fine: up to 7% global turnover                ║
╚══════════════════════════════════════════════════════════╝
```

## File Structure

```
eu-shield/
├── README.md
├── audit.py                 # Core compliance auditor
├── requirements/
│   ├── risk_classification.py  # Art. 6-7 risk classification
│   ├── data_governance.py      # Art. 10 data governance
│   ├── documentation.py        # Art. 11 technical docs
│   ├── transparency.py         # Art. 13, 50 transparency
│   ├── human_oversight.py      # Art. 14 human oversight
│   ├── accuracy_robustness.py  # Art. 15 accuracy/robustness
│   ├── conformity.py           # Art. 48 conformity assessment
│   ├── incident_reporting.py   # Art. 73 incident reporting
│   └── gpai.py                 # GPAI-specific requirements
├── templates/
│   ├── report.html             # HTML report template
│   └── declaration.md          # EU declaration of conformity
├── CHECKLIST.md
└── CONTRIBUTING.md
```

## CHECKLIST.md — Biweekly Review (Until Aug 2, 2026)

- [ ] Re-run audit on all high-risk AI systems
- [ ] Update data provenance documentation for any new training data
- [ ] Verify incident reporting mechanism is operational
- [ ] Check if any AI system crossed into "high-risk" classification
- [ ] Review EU AI Act implementing acts published since last check
- [ ] Confirm conformity assessment body engagement (if required)
- [ ] Update technical documentation for model changes
- [ ] Monitor member state transposition laws
- [ ] Verify GPAI code of practice compliance (if applicable)
- [ ] Calculate risk exposure: outstanding gaps × potential fines
