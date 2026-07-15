# Contributing to AI Security Toolkit

## Structure

Each product in this toolkit is **self-contained** in its own directory. You can:
- Use them independently (clone individual folders)
- Use them as Git submodules
- Fork the entire toolkit

## Adding a New Product

1. Create a directory with the product name: `mkdir <product-name>/`
2. Include at minimum:
   - `README.md` — Problem, features, quick start, file structure
   - `CHECKLIST.md` — Periodic review checklist (weekly/monthly/quarterly)
   - Core implementation script (Python, shell, or whatever fits)
3. Link it from the master `README.md`

## Updating Patterns

AI agents evolve weekly. When a new coding agent or AI tool gains adoption:
1. Check its credential/output patterns
2. Add detection rules to the relevant product
3. Update CHECKLIST.md with new review items

## Pull Request Process

1. Test your changes: each tool should run with `python3 <tool>/<script>.py --help`
2. Update the relevant CHECKLIST.md if your change affects review cadence
3. Ensure all file references and cross-links are correct

## Security

- Never commit real secrets or API keys to this repo
- Do not add patterns that produce excessive false positives
- Test new regex against both positive and negative test cases
