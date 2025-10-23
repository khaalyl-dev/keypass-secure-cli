#!/bin/bash
# Script to upload myapp-secure-cli to PyPI

echo "🚀 Uploading myapp-secure-cli to PyPI..."

# Check if twine is installed
if ! command -v twine &> /dev/null; then
    echo "Installing twine..."
    pip install twine
fi

# Check if dist files exist
if [ ! -d "dist" ]; then
    echo "❌ No dist/ folder found. Run ./build.sh first."
    exit 1
fi

echo "📦 Distribution files ready:"
ls -la dist/

echo ""
echo "🔐 You need PyPI credentials to upload:"
echo "1. Go to https://pypi.org/account/register/ to create account"
echo "2. Create API token at https://pypi.org/manage/account/"
echo "3. Use the token as password when prompted"
echo ""

# Upload to PyPI
echo "Uploading to PyPI..."
python3 -m twine upload dist/*

echo ""
echo "✅ Upload complete!"
echo "📋 Your package will be available at:"
echo "   https://pypi.org/project/myapp-secure-cli/"
echo ""
echo "🔧 Install from anywhere with:"
echo "   pip install myapp-secure-cli"
echo ""
echo "🧪 Test installation:"
echo "   pip install myapp-secure-cli"
echo "   myapp --help"