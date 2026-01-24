#!/bin/bash

# PyInstaller build script for SSH Client
# Usage: ./build.sh

set -e

echo "=== SSH Client Build Script ==="
echo "Building portable executable with PyInstaller..."

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist *.egg-info

# Build the executable
echo "Building executable..."
pyinstaller build.spec

# Copy optional config files to dist folder (if they exist)
echo "Copying config files..."
cp policies.json dist/ssh-client/ 2>/dev/null || true
cp totp_secrets.json dist/ssh-client/ 2>/dev/null || true
cp zt_ssh.db dist/ssh-client/ 2>/dev/null || true

echo ""
echo "=== Build Complete ==="
echo "Executable location: dist/ssh-client/ssh-client"
echo "All config files are in: dist/ssh-client/"
echo ""
echo "To run the application:"
echo "  cd dist/ssh-client"
echo "  ./ssh-client"
echo ""
echo "To create a portable archive:"
echo "  cd dist && zip -r ssh-client.zip ssh-client/"
echo ""