# VulnGate — Monthly Review Checklist

> **Why:** AI-generated vulnerability reports evolve with LLM capabilities. Attackers use AI to mass-file low-quality reports.

## Monthly

- [ ] Review auto-classified "AI-generated" reports for accuracy
- [ ] Update AI report classifier with new LLM output patterns
  - Check ChatGPT, Claude, Gemini output patterns
  - Look for new variations of "as an AI" circumvention
- [ ] Update trace parsers for new sanitizer formats
  - New ASAN, UBSan, MSan, CFI output formats
- [ ] Verify sandbox execution is not escaping containment
- [ ] Audit auto-closed issues — any false negatives (real vulns closed)?
- [ ] Update evidence scoring weights based on team feedback
- [ ] Review PoC compilation success rate in sandbox

## Quarterly

- [ ] Add trace parsers for new safety tools (KASan, syzkaller output)
- [ ] Review false negative rate: AI-generated vulns that passed gate
- [ ] Benchmark against CVE database for new proof formats
- [ ] Update auto-close message templates
