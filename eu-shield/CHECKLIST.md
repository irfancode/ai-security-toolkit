# EUShield — Biweekly Review Checklist (URGENT: Aug 2, 2026 Deadline)

> **Why:** The EU AI Act deadline is August 2, 2026. Non-compliance risks up to 7% global turnover fines.

## Biweekly (Until Aug 2, 2026)

- [ ] Re-run audit on ALL high-risk AI systems
  ```bash
  for manifest in manifests/*.json; do
    python3 eu-shield/audit.py --manifest "$manifest" --format html --output "reports/$(basename $manifest .json).html"
  done
  ```
- [ ] Update data provenance documentation for any new training data
- [ ] Verify incident reporting mechanism is operational (Art. 73)
- [ ] Check if any AI system crossed into "high-risk" classification
- [ ] Review EU AI Act implementing acts published since last check
- [ ] Confirm notified body engagement for high-risk systems
- [ ] Update technical documentation for model changes (Art. 11)
- [ ] Review GPAI code of practice compliance

## Monthly

- [ ] Calculate risk exposure: outstanding gaps × potential fines
- [ ] Run mock supervisory authority inspection
- [ ] Update conformity assessment documentation
- [ ] Verify CE marking application (if required)
- [ ] Review member state transposition laws
- [ ] Train teams on new regulatory requirements

## Post-Deadline (After Aug 2, 2026)

- [ ] Verify all high-risk systems are fully compliant
- [ ] Establish continuous compliance monitoring
- [ ] Schedule annual conformity reassessment
- [ ] Monitor for enforcement actions and regulatory guidance
