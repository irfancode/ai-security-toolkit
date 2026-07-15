#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys
from pathlib import Path

PATTERN_DIR = Path(__file__).parent / "patterns"
IGNORE_MARKER = "seal-skip-line"

def load_patterns():
    patterns = {}
    for pf in PATTERN_DIR.glob("*.json"):
        with open(pf) as f:
            data = json.load(f)
            patterns[pf.stem] = data.get("patterns", [])
    return patterns

def compile_regexes(patterns_dict):
    compiled = {}
    for category, pat_list in patterns_dict.items():
        compiled[category] = [(p["name"], re.compile(p["regex"]), p.get("severity", "medium"), p.get("message", "")) for p in pat_list]
    return compiled

def scan_file(filepath, compiled_patterns, ignore_paths=None):
    if ignore_paths and any(filepath.match(ip) for ip in ignore_paths):
        return []
    try:
        with open(filepath, "r", errors="ignore") as f:
            lines = f.readlines()
    except Exception:
        return []

    findings = []
    for lineno, line in enumerate(lines, 1):
        if IGNORE_MARKER in line:
            continue
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", "//", "--", "*", ";")):
            continue
        for category, patterns in compiled_patterns.items():
            for name, regex, severity, message in patterns:
                if regex.search(stripped):
                    findings.append({
                        "file": str(filepath),
                        "line": lineno,
                        "category": category,
                        "rule": name,
                        "severity": severity,
                        "message": message,
                        "match": regex.findall(stripped)[0] if regex.findall(stripped) else ""
                    })
    return findings

def scan_path(path, compiled_patterns, ignore_paths):
    path = Path(path)
    if path.is_file():
        return scan_file(path, compiled_patterns, ignore_paths)
    findings = []
    for f in path.rglob("*"):
        if f.is_file() and not f.name.startswith("."):
            findings.extend(scan_file(f, compiled_patterns, ignore_paths))
    return findings

def format_output(findings, fmt="text"):
    if fmt == "json":
        return json.dumps({"secrets": findings, "count": len(findings)}, indent=2)
    lines = [f"🔒 SealSecurity — {len(findings)} potential secrets found\n"]
    for f in findings:
        lines.append(f"  [{f['severity'].upper()}] {f['file']}:{f['line']}")
        lines.append(f"    Rule: {f['rule']} ({f['category']})")
        lines.append(f"    {f['message']}")
        lines.append("")
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="SealSecurity — Secrets scanner for agentic code")
    parser.add_argument("scan", nargs="?", help="Scan command")
    parser.add_argument("--path", default=".", help="Path to scan")
    parser.add_argument("--format", choices=["text", "json", "sarif"], default="text")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--ignore", help="Comma-separated glob patterns to ignore")
    parser.add_argument("--threshold", choices=["low", "medium", "high", "critical"], default="low")
    parser.add_argument("--exit-code", action="store_true", help="Exit non-zero if secrets found")

    args = parser.parse_args()

    if args.scan != "scan":
        config_mode(args)
        return

    patterns = load_patterns()
    compiled = compile_regexes(patterns)
    ignore_paths = [Path(p.strip()) for p in args.ignore.split(",")] if args.ignore else []

    findings = scan_path(args.path, compiled, ignore_paths)

    severity_order = {"low": 0, "medium": 1, "high": 2, "critical": 3}
    threshold_val = severity_order.get(args.threshold, 0)
    filtered = [f for f in findings if severity_order.get(f["severity"], 0) >= threshold_val]

    output = format_output(filtered, args.format)
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Results written to {args.output}")
    else:
        print(output)

    if args.exit_code and len(filtered) > 0:
        sys.exit(1)

def config_mode(args):
    if args.scan == "init":
        print("🔒 SealSecurity initialized. Add patterns to seal-security/patterns/")
    elif args.scan == "scan":
        pass
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
