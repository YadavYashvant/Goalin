#!/usr/bin/env bash
# Quick start script for Goalin

set -e

echo "╔════════════════════════════════════════╗"
echo "║   Goalin - Quick Start Setup          ║"
echo "╚════════════════════════════════════════╝"
echo ""

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "❌ Error: Goalin only supports Linux"
    exit 1
fi

echo "📋 Checking dependencies..."

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✓ Python $PYTHON_VERSION found"

# Check for pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed"
    exit 1
fi
echo "✓ pip3 found"

# Check for GTK4 (optional)
if pkg-config --exists gtk4; then
    echo "✓ GTK4 found"
else
    echo "⚠ GTK4 not found - GUI will not work"
fi

echo ""
echo "📦 Installing Goalin..."
pip3 install --user --break-system-packages .

echo ""
echo "⚙️  Setting up systemd service..."
mkdir -p ~/.config/systemd/user/
cp goalin.service ~/.config/systemd/user/
systemctl --user daemon-reload

echo ""
echo "🖥️  Installing desktop entry..."
mkdir -p ~/.local/share/applications/
cp goalin.desktop ~/.local/share/applications/
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database ~/.local/share/applications/
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Next steps:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1️⃣  Start the tracking daemon:"
echo "   systemctl --user start goalin.service"
echo ""
echo "2️⃣  Enable auto-start on login:"
echo "   systemctl --user enable goalin.service"
echo ""
echo "3️⃣  Launch the GUI application:"
echo "   goalin-gui"
echo ""
echo "4️⃣  Check daemon status:"
echo "   systemctl --user status goalin.service"
echo ""
echo "5️⃣  View logs:"
echo "   journalctl --user -u goalin.service -f"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Would you like to start the daemon now? (y/n)"
read -r response

if [[ "$response" =~ ^[Yy]$ ]]; then
    systemctl --user start goalin.service
    systemctl --user enable goalin.service
    echo ""
    echo "✅ Daemon started and enabled!"
    echo ""
    systemctl --user status goalin.service --no-pager
fi

echo ""
echo "🎉 Setup complete! Enjoy using Goalin!"
