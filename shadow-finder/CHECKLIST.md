# ShadowFinder — Weekly Review Checklist

> **Why:** Shadow AI proliferates fast. New LLM servers, agent frameworks, and AI tools launch weekly.

## Weekly

- [ ] Review latest scan results for new shadow AI assets
- [ ] Cross-reference discovered endpoints with approved asset inventory
- [ ] Follow up on any `critical` shadow_score assets (exposed + unauthenticated)
- [ ] Verify monitoring webhook is delivering alerts to Slack/Teams/PagerDuty

## Monthly

- [ ] Run a full multi-cloud scan
  ```bash
  python3 shadow-finder/scan.py --provider all --output full-shadow-report.json
  ```
- [ ] Update LLM endpoint signatures for new server versions
  - vLLM, TGI, Ollama, LocalAI, Triton, Ray Serve
- [ ] Scan container registries for unapproved AI images
- [ ] Review AI framework detection patterns for new releases
  - LangGraph, CrewAI, AutoGen, Semantic Kernel updates
- [ ] Check cloud provider AI service additions
  - New AWS/Azure/GCP AI services need detection rules

## Quarterly

- [ ] Full K8s cluster scan for AI workloads
- [ ] Audit compliance with tagging policies
- [ ] Pen-test discovered endpoints to verify auth requirements
- [ ] Inventory review: approve or decommission shadow assets
