#!/usr/bin/env python3
import argparse
import json
import os
import socket
import ssl
import sys
import urllib.request
from datetime import datetime
from pathlib import Path


def probe_endpoint(host: str, port: int, path: str, timeout: int = 5) -> dict:
    result = {"host": host, "port": port, "path": path, "open": False, "requires_auth": True, "service": None}
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        url = f"https://{host}:{port}{path}" if port == 443 else f"http://{host}:{port}{path}"
        req = urllib.request.Request(url, method="GET", headers={"User-Agent": "ShadowFinder/1.0"})
        resp = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        result["open"] = True
        result["status"] = resp.status
        body = resp.read().decode("utf-8", errors="ignore")[:500]
        if "chat/completions" in path:
            result["service"] = "openai-compatible-api"
        if "Unauthorized" not in body and "401" not in body and "403" not in body:
            result["requires_auth"] = False
        return result
    except urllib.error.HTTPError as e:
        if e.code == 401 or e.code == 403:
            result["open"] = True
            result["requires_auth"] = True
            result["status"] = e.code
            result["service"] = "openai-compatible-api"
            return result
        return result
    except Exception:
        return result


def scan_network_range(cidr: str, ports: list):
    return []


def scan_k8s(kubeconfig: str = None):
    return []


def scan_aws(regions: list = None):
    return []


def scan_azure():
    return []


def scan_gcp():
    return []


def discover_llm_endpoints(targets: list) -> list:
    endpoints = [
        "/v1/chat/completions",
        "/v1/completions",
        "/v1/models",
        "/v1/embeddings",
        "/api/generate",
        "/api/chat",
        "/health",
        "/metrics",
    ]
    results = []
    for target in targets:
        host = target.get("host", "localhost")
        for port in target.get("ports", [8000, 8080, 443, 80, 3000, 5000, 11434]):
            for path in endpoints:
                result = probe_endpoint(host, port, path)
                if result["open"]:
                    results.append(result)
    return results


def score_asset(asset: dict) -> int:
    score = 0
    if not asset.get("tags"):
        score += 30
    if asset.get("exposed"):
        score += 40
    if not asset.get("requires_auth", True):
        score += 25
    if asset.get("source") == "shadow":
        score += 50
    return min(score, 100)


def generate_recommendations(assets: list) -> list:
    recs = []
    for a in assets:
        if a.get("shadow_score", 0) >= 70:
            recs.append(f"CRITICAL: Shadow AI asset {a.get('id', 'unknown')} ({a.get('endpoint', 'N/A')}) — restrict access immediately")
        elif a.get("shadow_score", 0) >= 40:
            recs.append(f"HIGH: Untagged AI resource {a.get('id', 'unknown')} — apply tags and verify authorization")
        if a.get("exposed") and not a.get("requires_auth", True):
            recs.append(f"INSECURE: {a.get('endpoint', 'N/A')} is publicly accessible with no authentication")
    return list(set(recs))


def main():
    parser = argparse.ArgumentParser(description="ShadowFinder — AI-SPM discovery scanner")
    parser.add_argument("--provider", default="aws", help="Cloud provider: aws, azure, gcp, k8s, all")
    parser.add_argument("--region", help="Cloud region (default: all)")
    parser.add_argument("--output", help="Output file path (JSON)")
    parser.add_argument("--kubeconfig", help="Path to kubeconfig file")
    parser.add_argument("--probe-targets", help="JSON file with host:port targets to probe for LLM endpoints")

    args = parser.parse_args()
    assets = []
    recommendations = []

    if args.probe_targets:
        with open(args.probe_targets) as f:
            targets = json.load(f)
        llm_results = discover_llm_endpoints(targets)
        for r in llm_results:
            asset = {
                "id": f"{r['host']}:{r['port']}{r['path']}",
                "provider": "custom",
                "service": r.get("service", "unknown"),
                "endpoint": f"http://{r['host']}:{r['port']}{r['path']}" if r['port'] != 443 else f"https://{r['host']}:{r['port']}{r['path']}",
                "exposed": True,
                "requires_auth": r.get("requires_auth", True),
                "source": "shadow",
                "tags": {},
            }
            asset["shadow_score"] = score_asset(asset)
            assets.append(asset)

    provider = args.provider.lower()
    if provider in ("aws", "all"):
        pass
    if provider in ("azure", "all"):
        pass
    if provider in ("gcp", "all"):
        pass
    if provider in ("k8s", "all") or args.kubeconfig:
        results = scan_k8s(args.kubeconfig)
        assets.extend(results)

    for a in assets:
        a["shadow_score"] = score_asset(a)
        if a["shadow_score"] >= 70:
            a["risk"] = "CRITICAL"
        elif a["shadow_score"] >= 40:
            a["risk"] = "HIGH"
        else:
            a["risk"] = "MEDIUM"

    recommendations = generate_recommendations(assets)
    shadow_count = sum(1 for a in assets if a.get("source") == "shadow")
    critical_count = sum(1 for a in assets if a.get("risk") == "CRITICAL")

    report = {
        "scan_id": f"sf-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "provider": provider,
        "total_assets": len(assets),
        "shadow_assets": shadow_count,
        "critical_exposures": critical_count,
        "assets": assets,
        "recommendations": recommendations,
    }

    output = json.dumps(report, indent=2)
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Report written to {args.output}")
    else:
        print(output)

    if critical_count > 0:
        print(f"\n⚠ CRITICAL: {critical_count} critically exposed AI assets found!")
        sys.exit(1)


if __name__ == "__main__":
    main()
