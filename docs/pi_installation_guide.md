# Raspberry Pi Installation Guide

Complete guide for installing and configuring ShokeDex on Raspberry Pi 3B+ or newer.

## Table of Contents

- [Prerequisites](#prerequisites)
- [OS Installation](#os-installation)
- [System Configuration](#system-configuration)
- [ShokeDex Installation](#shokedex-installation)
- [Hardware Setup](#hardware-setup)
- [Autostart Configuration](#autostart-configuration)
- [Updates and Maintenance](#updates-and-maintenance)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Hardware Requirements

**Required:**
- Raspberry Pi 3B+ or newer (Pi 4 recommended)
- MicroSD card (16GB or larger, Class 10 or better)
- Power supply (official Raspberry Pi power supply recommended)
- LCD display (see display options below)
- 6-8 tactile push buttons for input

**Optional:**
- USB keyboard and mouse (for setup)
- Ethernet cable or WiFi
- Battery pack for portable use
- 3D printed case

### Display Options

1. **Official Raspberry Pi 7" Touch Display** (800x480)
   - Best integration
   - Touch support (optional feature)
   - No additional drivers needed

2. **Waveshare 3.5" - 5" LCD** (480x320 or 800x480)
   - Compact size
   - SPI or GPIO connection
   - May require driver installation

3. **HDMI Display**
   - Any size/resolution
   - Easiest setup
   - Not portable

## OS Installation

### 1. Download Raspberry Pi OS

Download Raspberry Pi OS (Bookworm or newer):
- **Recommended:** Raspberry Pi OS Lite (64-bit) - headless, minimal install
- **Alternative:** Raspberry Pi OS with Desktop - if you want GUI access

Download from: https://www.raspberrypi.org/software/

### 2. Flash OS to SD Card

**Using Raspberry Pi Imager (Recommended):**

```bash
# Install Raspberry Pi Imager on your computer
# Windows: Download from raspberrypi.org
# macOS: brew install --cask raspberry-pi-imager
# Linux: sudo apt install rpi-imager

# Launch imager, select OS and SD card, then write
```

**Advanced Settings in Imager:**
- Enable SSH (if using headless)
- Set hostname: `shokedex.local`
- Configure WiFi credentials
- Set username/password

### 3. First Boot

```bash
# Insert SD card into Pi and power on
# Wait 1-2 minutes for first boot

# SSH into Pi (if headless)
ssh pi@shokedex.local
# Or use the username you configured
```

## System Configuration

### 1. Update System

```bash
# Update package lists
sudo apt update

# Upgrade installed packages
sudo apt full-upgrade -y

# Reboot
sudo reboot
```

### 2. Configure Raspberry Pi Settings

```bash
# Run configuration tool
sudo raspi-config

# Recommended settings:
# 1. System Options > Boot / Auto Login > Console Autologin (for autostart)
# 2. Interface Options > I2C > Enable (if using I2C display)
# 3. Interface Options > SPI > Enable (if using SPI display)
# 4. Performance Options > GPU Memory > 128 (for better graphics)
# 5. Localisation Options > Set timezone, locale, keyboard as needed
# 6. Advanced Options > Expand Filesystem
```

### 3. Install System Dependencies

```bash
# Install Python 3.11+ (usually pre-installed on Bookworm)
python3 --version

# Install system libraries for pygame and Pillow
sudo apt install -y \
    python3-pip \
    python3-pygame \
    python3-pil \
    python3-venv \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    git

# Install psutil for performance monitoring
sudo apt install -y python3-psutil
```

### 4. Configure Display (if using LCD)

**For Waveshare LCD displays:**

```bash
# Download and run the driver installation script
# Example for Waveshare 3.5" LCD:
git clone https://github.com/waveshare/LCD-show.git
cd LCD-show/
# Follow manufacturer's instructions for your specific model
# ./LCD35-show
```

**For Official Raspberry Pi Touch Display:**
- Should work out of the box, no additional configuration needed

**Test display:**

```bash
# Check if display is detected
tvservice -s

# For DSI displays:
cat /proc/device-tree/display/status
```

## ShokeDex Installation

### 1. Clone Repository

```bash
# Navigate to home directory
cd ~

# Clone the repository
git clone https://github.com/scwardbulldog/ShokeDex.git
cd ShokeDex
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### 3. Install Python Dependencies

```bash
# Install requirements
pip install -r requirements.txt

# Verify installation
python -c "import pygame, PIL, gpiozero, requests; print('All packages OK')"
```

### 4. Set Up Database

```bash
# Initialize database schema
python src/data/manage_db.py init

# Load Pokémon data (requires internet connection)
# This takes 10-20 minutes
python src/data/manage_db.py seed --gen 1-3

# Verify data loaded
python src/data/manage_db.py stats
```

### 5. Process Sprites (Optional)

```bash
# Download and process Pokémon sprites
# This creates optimized sprites for the display
python src/data/sprite_processor.py --all

# Sprites will be saved in:
# - assets/sprites/thumb/ (32x32)
# - assets/sprites/detail/ (96x96)
```

### 6. Test Installation

```bash
# Activate virtual environment if not already active
source ~/ShokeDex/venv/bin/activate

# Test with keyboard input (for testing)
python src/main.py

# Use arrow keys to navigate, ESC to exit
# Verify all screens work correctly
```

## Hardware Setup

### GPIO Button Wiring

**Default Pin Configuration (BCM numbering):**

| Button   | GPIO Pin | Physical Pin |
|----------|----------|--------------|
| UP       | GPIO 17  | Pin 11       |
| DOWN     | GPIO 27  | Pin 13       |
| LEFT     | GPIO 22  | Pin 15       |
| RIGHT    | GPIO 23  | Pin 16       |
| SELECT   | GPIO 24  | Pin 18       |
| BACK     | GPIO 25  | Pin 22       |
| START    | GPIO 16  | Pin 36       |

**Wiring Instructions:**

1. **For each button:**
   - Connect one side to the GPIO pin
   - Connect the other side to Ground (GND)
   - Add 10kΩ pull-up resistor between GPIO pin and 3.3V (optional, software pull-up used)

2. **Ground connections:**
   - Use physical pins: 6, 9, 14, 20, 25, 30, 34, 39 (all GND)

3. **Wiring Diagram:**
```
GPIO Pin  ----[Button]---- GND
         |
         [10kΩ Resistor] (optional)
         |
        3.3V
```

### Testing Buttons

```bash
# Test button wiring
python -c "from gpiozero import Button; b = Button(17); print('Press button...'); b.wait_for_press(); print('Button works!')"

# Test input latency
python tools/test_input_latency.py gpio
```

## Autostart Configuration

### Method 1: Systemd Service (Recommended)

Create a systemd service for automatic startup:

```bash
# Create service file
sudo nano /etc/systemd/system/shokedex.service
```

**Service file content:**

```ini
[Unit]
Description=ShokeDex Pokedex Application
After=multi-user.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/ShokeDex
Environment="DISPLAY=:0"
Environment="PYGAME_HIDE_SUPPORT_PROMPT=1"
ExecStart=/home/pi/ShokeDex/venv/bin/python /home/pi/ShokeDex/src/main.py
Restart=on-failure
RestartSec=5s
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Enable and start the service:**

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable shokedex.service

# Start service now
sudo systemctl start shokedex.service

# Check status
sudo systemctl status shokedex.service

# View logs
journalctl -u shokedex.service -f
```

**Service management commands:**

```bash
# Stop service
sudo systemctl stop shokedex.service

# Restart service
sudo systemctl restart shokedex.service

# Disable autostart
sudo systemctl disable shokedex.service

# View logs
journalctl -u shokedex.service --since "1 hour ago"
```

### Method 2: Autostart via .bashrc (Simple)

For console autologin:

```bash
# Edit .bashrc
nano ~/.bashrc

# Add to the end of the file:
if [ -z "$SSH_CLIENT" ] && [ -z "$SSH_TTY" ]; then
    cd ~/ShokeDex
    source venv/bin/activate
    python src/main.py
fi
```

### Method 3: Desktop Autostart (If using Desktop OS)

```bash
# Create autostart directory
mkdir -p ~/.config/autostart

# Create desktop entry
nano ~/.config/autostart/shokedex.desktop
```

**Desktop entry content:**

```ini
[Desktop Entry]
Type=Application
Name=ShokeDex
Exec=/home/pi/ShokeDex/venv/bin/python /home/pi/ShokeDex/src/main.py
Path=/home/pi/ShokeDex
Terminal=false
StartupNotify=false
```

## Updates and Maintenance

### Updating ShokeDex

```bash
# Navigate to ShokeDex directory
cd ~/ShokeDex

# Stop service if running
sudo systemctl stop shokedex.service

# Pull latest changes
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Update dependencies
pip install -r requirements.txt --upgrade

# Run database migrations if any
python src/data/manage_db.py migrate

# Restart service
sudo systemctl start shokedex.service
```

### Backup Configuration

```bash
# Backup database
cp ~/ShokeDex/data/pokedex.db ~/pokedex_backup_$(date +%Y%m%d).db

# Backup entire ShokeDex directory
tar -czf ~/shokedex_backup_$(date +%Y%m%d).tar.gz ~/ShokeDex

# Restore from backup
tar -xzf ~/shokedex_backup_YYYYMMDD.tar.gz
```

### System Maintenance

```bash
# Update Raspberry Pi OS
sudo apt update && sudo apt upgrade -y

# Clean up old packages
sudo apt autoremove -y
sudo apt autoclean

# Check disk space
df -h

# Check system logs
journalctl -p err --since "7 days ago"
```

## Troubleshooting

### Service Won't Start

```bash
# Check service status
sudo systemctl status shokedex.service

# Check logs for errors
journalctl -u shokedex.service -n 50

# Common issues:
# 1. Wrong file paths in service file
# 2. Virtual environment not activated
# 3. Missing DISPLAY environment variable
# 4. Permission issues
```

### Display Not Working

```bash
# Check if display is detected
tvservice -s

# Try setting DISPLAY variable
export DISPLAY=:0

# For framebuffer devices
export SDL_FBDEV=/dev/fb0
export SDL_VIDEODRIVER=fbcon

# Test pygame
python -c "import pygame; pygame.init(); print(pygame.display.list_modes())"
```

### Buttons Not Responding

```bash
# Test GPIO access
sudo gpiozero-info

# Check button with simple test
python -c "from gpiozero import Button; b = Button(17); b.wait_for_press(); print('OK')"

# Verify user is in gpio group
groups $USER
# If not, add user:
sudo usermod -a -G gpio $USER
# Then logout and login again
```

### Performance Issues

```bash
# Check CPU temperature
vcgencmd measure_temp

# Check throttling
vcgencmd get_throttled

# Monitor resources
htop

# Run performance profiler
cd ~/ShokeDex
source venv/bin/activate
python tools/profile_performance.py 60
```

### Network Issues (for data loading)

```bash
# Test internet connectivity
ping -c 4 pokeapi.co

# Check DNS
cat /etc/resolv.conf

# Test API access
curl https://pokeapi.co/api/v2/pokemon/1
```

## Post-Installation Checklist

- [ ] Raspberry Pi OS installed and updated
- [ ] Display working correctly
- [ ] ShokeDex cloned and dependencies installed
- [ ] Database initialized and data loaded
- [ ] Buttons wired and tested
- [ ] Application runs correctly with keyboard
- [ ] Application runs correctly with GPIO buttons
- [ ] Autostart configured and tested
- [ ] Performance meets targets (use profiling tools)
- [ ] Backup created

## Getting Help

If you encounter issues:

1. Check the logs: `journalctl -u shokedex.service -f`
2. Run performance profiling: `python tools/profile_performance.py`
3. Review [Pi Optimization Guide](pi_optimization_guide.md)
4. Check [Troubleshooting Guide](troubleshooting.md)
5. Open an issue on GitHub with logs and system info

## System Information Collection

When reporting issues, include:

```bash
# System info
uname -a
cat /etc/os-release
python3 --version

# Pi model
cat /proc/device-tree/model

# Memory and CPU
free -h
lscpu

# Display info
tvservice -s

# GPIO info (if button issues)
gpio readall
```

---

**Happy Building!** Your ShokeDex is ready to run on Raspberry Pi! 🎮✨
