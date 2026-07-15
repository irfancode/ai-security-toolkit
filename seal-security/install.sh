#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="${HOME}/.seal-security"

echo "🔒 Installing SealSecurity..."

mkdir -p "${INSTALL_DIR}/patterns"
cp -r "${SCRIPT_DIR}/seal.py" "${INSTALL_DIR}/"
cp -r "${SCRIPT_DIR}/patterns/"* "${INSTALL_DIR}/patterns/"
cp "${SCRIPT_DIR}/action.yml" "${INSTALL_DIR}/" 2>/dev/null || true

# Make seal.py executable
chmod +x "${INSTALL_DIR}/seal.py"

# Create wrapper script
cat > /usr/local/bin/seal-security << 'WRAPPER'
#!/bin/bash
exec python3 "${HOME}/.seal-security/seal.py" "$@"
WRAPPER
chmod +x /usr/local/bin/seal-security

echo "✅ SealSecurity installed to ${INSTALL_DIR}"
echo "   Run 'seal-security scan --path .' to scan your project"
echo ""
echo "To install the pre-commit hook:"
echo "  seal-security init"
echo "  # Then add the hook script to .git/hooks/pre-commit"
