#!/bin/bash
# Build script for myapp distribution

echo "🔨 Building myapp distribution package..."

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/
rm -rf dist/
rm -rf *.egg-info/

# Install build dependencies
echo "Installing build dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install build wheel

# Build the package
echo "Building package..."
python3 -m build

echo "✅ Build complete!"
echo ""
echo "📦 Distribution files created in dist/:"
ls -la dist/

echo ""
echo "🚀 To install:"
echo "pip install dist/myapp-secure-cli-0.1.0-py3-none-any.whl"
