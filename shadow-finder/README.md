# ShadowFinder — AI Security Posture Management (AI-SPM)

> *"1 in 4 organizations suffer from 'Shadow AI' — running LLM instances and AI workloads they don't know about."* — Orca Security, State of AI Security Report 2026
> *"Over 60% of security practitioners have zero visibility into where AI models are running."* — SANS 2026 AI Survey

**ShadowFinder** discovers running LLM instances, AI models, agentic workloads, and AI infrastructure across your cloud environments — because you can't secure what you can't see.

## The Problem

- Teams deploy AI models without informing security
- LLM endpoints (OpenAI-compatible, vLLM, TGI, Ollama, etc.) run on unsecured cloud instances
- AI agents spin up infrastructure dynamically with no tagging or governance
- 99.9% of fixable AI vulnerabilities remain unpatched

## Features

- **Multi-Cloud Discovery** — Scans AWS, Azure, GCP for AI/ML services and custom deployments
- **LLM Endpoint Detection** — Probes for open API endpoints (OpenAI, vLLM, TGI, Ollama, Ray Serve, BentoML)
- **Agent Workload Discovery** — Detects agentic frameworks (LangChain, CrewAI, AutoGen, Semantic Kernel)
- **Container/Orchestration Scan** — Finds AI containers in ECS, AKS, GKE, and self-managed Kubernetes
- **Exposure Assessment** — Checks if AI endpoints are publicly accessible or require auth
- **Model Inventory** — Builds a searchable inventory of all AI/ML resources
- **Shadow Scoring** — Ranks discovered assets by risk (unknown + publicly exposed = critical)

## Quick Start

```bash
# Install
pip install -r shadow-finder/requirements.txt

# Quick scan (AWS default)
python3 shadow-finder/scan.py --provider aws --region us-east-1

# Full multi-cloud scan
python3 shadow-finder/scan.py --provider all --output shadow-report.json

# Kubernetes cluster scan
python3 shadow-finder/scan.py --provider k8s --kubeconfig ~/.kube/config

# Continuous monitoring
python3 shadow-finder/monitor.py --interval 3600 --webhook https://hooks.slack.com/...
```

## Discovery Capabilities

### Cloud Provider AI Services

| Provider | Services Scanned |
|---|---|
| **AWS** | SageMaker, Bedrock, ECS/EKS with AI images, EC2 GPU instances, Lambda with AI deps |
| **Azure** | OpenAI Service, AI Studio, ML Studio, Container Instances, AKS |
| **GCP** | Vertex AI, AI Platform, GKE GPU nodes, Cloud Run, Compute Engine GPU |

### Custom/OSS LLM Endpoints

- OpenAI-compatible API endpoints (`/v1/chat/completions`, `/v1/completions`)
- vLLM, Text Generation Inference (TGI), Ollama, LocalAI
- Ray Serve, BentoML, Triton Inference Server
- LangChain, LlamaIndex, Haystack apps

### Framework Detection

Searches source code and running processes for:
- LangChain, LangGraph, CrewAI, AutoGen, Semantic Kernel
- DSPy, Haystack, LlamaIndex
- OpenAI/Anthropic/Cohere SDK usage

## Example Output

```json
{
  "scan_id": "sf-20260715-001",
  "timestamp": "2026-07-15T14:30:00Z",
  "total_assets": 47,
  "shadow_assets": 12,
  "critical_exposures": 3,
  "assets": [
    {
      "id": "i-0abcd1234efgh5678",
      "provider": "aws",
      "service": "ec2",
      "region": "us-east-1",
      "tags": {},
      "open_ports": [8080, 443, 22],
      "ai_signature": "vllm",
      "endpoint": "http://54.123.45.67:8080/v1/chat/completions",
      "exposed": true,
      "requires_auth": false,
      "shadow_score": 95,
      "risk": "CRITICAL"
    }
  ],
  "recommendations": [
    "Restrict ingress on i-0abcd1234efgh5678 (vLLM endpoint publicly accessible, no auth)",
    "Apply 'managed-by: security' tag to shadow resource i-0abcd1234efgh5678",
    "12 untagged AI resources found — implement tagging policy"
  ]
}
```

## Check List Template

```json
{
  "org": "example-corp",
  "scan_date": "2026-07-15",
  "checks": [
    {"id": "SF-001", "check": "All AI endpoints require authentication", "status": "fail"},
    {"id": "SF-002", "check": "No publicly exposed LLM inference APIs", "status": "fail"},
    {"id": "SF-003", "check": "All AI resources have owner/team tags", "status": "fail"},
    {"id": "SF-004", "check": "GPU instances are in private subnets", "status": "pass"},
    {"id": "SF-005", "check": "Model registries are access-controlled", "status": "pass"}
  ]
}
```

## File Structure

```
shadow-finder/
├── README.md
├── scan.py              # Core scanner
├── monitor.py           # Continuous monitoring loop
├── requirements.txt     # Dependencies
├── providers/
│   ├── aws.py           # AWS discovery
│   ├── azure.py         # Azure discovery
│   ├── gcp.py           # GCP discovery
│   └── k8s.py           # Kubernetes discovery
├── detectors/
│   ├── llm_endpoint.py  # Open LLM API endpoint probe
│   ├── framework.py     # AI framework detection
│   └── container.py     # Container image analysis
├── reports/
│   ├── inventory.py     # Model inventory builder
│   └── exposure.py      # Exposure assessment
├── CHECKLIST.md
└── CONTRIBUTING.md
```

## CHECKLIST.md — Weekly Review

- [ ] Review latest scan for new shadow AI assets
- [ ] Cross-reference discovered endpoints with approved asset inventory
- [ ] Follow up on any `critical` shadow_score assets
- [ ] Update AI endpoint signatures for new LLM server versions
- [ ] Verify monitoring webhook is delivering alerts
- [ ] Run a full multi-cloud scan at least monthly
- [ ] Review container registries for unapproved AI images
