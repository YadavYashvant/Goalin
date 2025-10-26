# Installation Guide for Goalin

This guide provides detailed installation instructions for different scenarios.

## Table of Contents

- [Arch Linux (AUR)](#arch-linux-aur)
- [Other Linux Distributions](#other-linux-distributions)
- [Development Installation](#development-installation)
- [Post-Installation Setup](#post-installation-setup)
- [Troubleshooting](#troubleshooting)

## Arch Linux (AUR)

### Using an AUR Helper

The easiest way to install on Arch Linux is using an AUR helper:

#### yay
```bash
yay -S goalin
```

#### paru
```bash
paru -S goalin
```

### Manual Installation from AUR

```bash
# Install base-devel if not already installed
sudo pacman -S base-devel

# Clone the AUR repository
git clone https://aur.archlinux.org/goalin.git
cd goalin

# Build and install
makepkg -si
```

## Other Linux Distributions

### Prerequisites

First, install the required dependencies:

#### Debian/Ubuntu
```bash
sudo apt update
sudo apt install python3 python3-pip python3-gi python3-gi-cairo \
                 gir1.2-gtk-4.0 gir1.2-adw-1 python3-xlib
```

#### Fedora
```bash
sudo dnf install python3 python3-pip python3-gobject gtk4 \
                 libadwaita python3-xlib
```

#### openSUSE
```bash
sudo zypper install python3 python3-pip python3-gobject \
                    gtk4 libadwaita python3-xlib
```

### Install Goalin

```bash
# Clone the repository
git clone https://github.com/YadavYashvant/Goalin.git
cd Goalin

# Install Python dependencies
pip3 install --user -r requirements.txt

# Install the package
pip3 install --user .

# Or use setup.py directly
python3 setup.py install --user
```

## Development Installation

For development, it's recommended to use a virtual environment:

```bash
# Clone the repository
git clone https://github.com/YadavYashvant/Goalin.git
cd Goalin

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On fish: source venv/bin/activate.fish

# Install in editable mode
pip install -e .

# Install development dependencies
pip install pytest pylint black
```

## Post-Installation Setup

### 1. Install Systemd Service

```bash
# Create systemd user directory if it doesn't exist
mkdir -p ~/.config/systemd/user/

# Copy service file
cp goalin.service ~/.config/systemd/user/

# Reload systemd
systemctl --user daemon-reload

# Enable service to start on login
systemctl --user enable goalin.service

# Start service immediately
systemctl --user start goalin.service
```

### 2. Verify Service Status

```bash
# Check if service is running
systemctl --user status goalin.service

# View logs
journalctl --user -u goalin.service -f
```

### 3. Install Desktop Entry

```bash
# Create applications directory if needed
mkdir -p ~/.local/share/applications/

# Copy desktop file
cp goalin.desktop ~/.local/share/applications/

# Update desktop database
update-desktop-database ~/.local/share/applications/
```

### 4. Launch GUI

```bash
# From terminal
goalin-gui

# Or find "Goalin" in your application launcher
```

## Troubleshooting

### Service Won't Start

1. Check the service status:
   ```bash
   systemctl --user status goalin.service
   ```

2. View detailed logs:
   ```bash
   journalctl --user -u goalin.service -b
   ```

3. Ensure Python dependencies are installed:
   ```bash
   pip3 list | grep -E "PyGObject|xlib|pytz"
   ```

### GUI Won't Launch

1. Check if GTK4 and libadwaita are installed:
   ```bash
   # Arch
   pacman -Q gtk4 libadwaita
   
   # Debian/Ubuntu
   dpkg -l | grep -E "gtk-4|libadwaita"
   ```

2. Test with verbose output:
   ```bash
   G_MESSAGES_DEBUG=all goalin-gui
   ```

### X11 Window Tracking Not Working

1. Ensure python-xlib is installed:
   ```bash
   pip3 show python-xlib
   ```

2. Check if DISPLAY variable is set:
   ```bash
   echo $DISPLAY
   ```

3. Test X11 connection:
   ```bash
   xprop -root | grep "^_NET_ACTIVE_WINDOW"
   ```

### Wayland Tracking Issues

Wayland has security restrictions that limit window tracking. For best results:

1. Use Sway compositor:
   ```bash
   swaymsg -t get_tree
   ```

2. Install sway-related tools:
   ```bash
   sudo pacman -S sway swayidle  # Arch
   ```

### Database Errors

1. Check database file permissions:
   ```bash
   ls -la ~/.local/share/goalin/activity.db
   ```

2. Reset database (WARNING: deletes all data):
   ```bash
   rm ~/.local/share/goalin/activity.db
   systemctl --user restart goalin.service
   ```

### High CPU Usage

1. Adjust polling interval in `~/.local/lib/python3.*/site-packages/goalin/config.py`:
   ```python
   POLL_INTERVAL = 10  # Increase from 5 to 10 seconds
   ```

2. Restart the service:
   ```bash
   systemctl --user restart goalin.service
   ```

## Uninstallation

### AUR Installation
```bash
yay -R goalin
# or
paru -R goalin
```

### Manual Installation
```bash
# Stop and disable service
systemctl --user stop goalin.service
systemctl --user disable goalin.service

# Remove service file
rm ~/.config/systemd/user/goalin.service
systemctl --user daemon-reload

# Uninstall Python package
pip3 uninstall goalin

# Remove desktop entry
rm ~/.local/share/applications/goalin.desktop
update-desktop-database ~/.local/share/applications/

# Remove data (optional - includes all reports and database)
rm -rf ~/.local/share/goalin
rm -rf ~/.config/goalin
rm -rf ~/.cache/goalin
```

## Getting Help

If you encounter issues not covered here:

1. Check existing [GitHub Issues](https://github.com/YadavYashvant/Goalin/issues)
2. Create a new issue with:
   - Your Linux distribution and version
   - Desktop environment and display server (X11/Wayland)
   - Output of `systemctl --user status goalin.service`
   - Relevant log entries
3. Join discussions in the [Discussions](https://github.com/YadavYashvant/Goalin/discussions) section
