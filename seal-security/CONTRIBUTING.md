# Contributing to SealSecurity

## How to Add New Patterns

1. Add your regex pattern to the appropriate file in `patterns/`
2. Follow the format:
   ```json
   {"name": "descriptive-name", "regex": "your-regex", "severity": "critical|high|medium|low", "message": "Description of what was found"}
   ```
3. Run tests: `python3 seal.py scan --path test/fixtures/`
4. Ensure no false positives on test fixtures

## Agent Pattern Updates

AI agents change behavior frequently. If you notice:
- A new AI coding tool generating credentials in a novel format
- A pattern that's no longer being produced
- A new cloud provider credential format

Please submit a PR updating `patterns/agent.json`.

## Testing

```bash
python3 -m pytest tests/
python3 seal.py scan --path . --format json
```
