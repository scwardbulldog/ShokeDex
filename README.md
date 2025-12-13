# ShokeDex

**Shane's Pokédex Clone - A Raspberry Pi Project**

A handheld Pokédex device built on Raspberry Pi that displays Pokémon information, complete with LCD display and interactive controls.

## 📋 Table of Contents

- [Overview](#overview)
- [Goals](#goals)
- [Tech Stack](#tech-stack)
- [Hardware Requirements](#hardware-requirements)
- [Software Requirements](#software-requirements)
- [Setup Instructions](#setup-instructions)
- [Project Structure](#project-structure)
- [Development](#development)
- [License](#license)

## 🎯 Overview

ShokeDex is a physical Pokédex implementation designed to run on a Raspberry Pi with an LCD display. Users can browse Pokémon, view detailed information, and interact with the device using physical buttons connected via GPIO.

## 🎮 Goals

- Create an interactive, handheld Pokédex experience
- Display Pokémon sprites, stats, and information
- Implement intuitive navigation using physical buttons
- Store Pokémon data locally in a SQLite database
- Fetch updated Pokémon information from online APIs
- Design a responsive UI optimized for small LCD screens
- Build a portable, battery-powered device

## 🛠️ Tech Stack

### Software
- **Python 3.11+** - Primary programming language
- **pygame** - Graphics rendering and display management
- **Pillow (PIL)** - Image processing and manipulation
- **sqlite3** - Local database for Pokémon data (Python standard library)
- **requests** - HTTP client for API calls
- **gpiozero** - GPIO interface for button controls

### Hardware
- **Raspberry Pi** (Model 3B+ or newer recommended)
- **LCD Display** - See [Hardware Requirements](#hardware-requirements)
- **Physical Buttons** - Connected via GPIO pins
- **Power Supply** - Battery pack or USB power

## 💻 Hardware Requirements

### Raspberry Pi
- **Model**: Raspberry Pi 3B+ or newer (Raspberry Pi 4 recommended for better performance)
- **OS**: Raspberry Pi OS (Bookworm - Debian 12 based) or newer
  - Recommended: Raspberry Pi OS Lite (64-bit) for headless operation
  - Full desktop version also supported
- **RAM**: Minimum 1GB (2GB+ recommended)
- **Storage**: 8GB+ microSD card

### Display Options
The project is designed to work with common LCD displays:

1. **Official Raspberry Pi Touch Display (7")**
   - Resolution: 800x480
   - Interface: DSI connector
   - Touch support included

2. **Small TFT LCD Displays (3.5" - 5")**
   - Resolution: 480x320 or 800x480
   - Interface: SPI or GPIO
   - Popular models: Adafruit PiTFT, Waveshare LCD displays

3. **HDMI Displays**
   - Any HDMI-compatible display
   - Various resolutions supported

### GPIO Components
- **Navigation Buttons**: 4-6 tactile buttons for D-pad navigation
- **Action Buttons**: 2-4 buttons for selection/back actions
- **Resistors**: 10kΩ pull-down resistors for each button
- **Breadboard/PCB**: For prototyping or final assembly

## 📦 Software Requirements

### Python Version
- Python 3.11 or higher (Python 3.12 supported)

### Operating System
- **Raspberry Pi OS** (Bookworm - December 2023 or newer)
  - Based on Debian 12
  - Kernel version 6.1+
- Alternative: Ubuntu Server 22.04 LTS for ARM

### Dependencies
All Python dependencies are listed in `requirements.txt`. Key libraries:
- pygame (2.5.0+)
- Pillow (10.0.0+)
- gpiozero (2.0.0+)
- requests (2.31.0+)

## 🚀 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/scwardbulldog/ShokeDex.git
cd ShokeDex
```

### 2. Set Up Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Linux/macOS
# or
venv\Scripts\activate  # On Windows
```

### 3. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install required packages
pip install -r requirements.txt
```

### 4. Verify Installation

```bash
# Check Python version
python --version  # Should be 3.11+

# Verify key packages
python -c "import pygame; import PIL; import gpiozero; import requests; print('All packages imported successfully!')"
```

### 5. Configure Raspberry Pi (On Device)

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install system dependencies for pygame and Pillow
sudo apt install -y python3-pygame python3-pil libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev

# Enable required interfaces (if using GPIO)
sudo raspi-config
# Navigate to: Interface Options -> Enable I2C, SPI (if needed)
```

### 6. Hardware Setup

1. Connect your LCD display according to manufacturer instructions
2. Wire physical buttons to GPIO pins (default configuration in `src/config.py`)
3. Ensure proper pull-down resistors are connected
4. Test button connections with the GPIO testing script (coming soon)

## 📁 Project Structure

```
ShokeDex/
├── src/                    # Source code
│   ├── __init__.py        # Package initialization
│   ├── main.py            # Application entry point
│   ├── input_manager.py   # Input abstraction (GPIO & keyboard)
│   ├── ui/                # User interface modules
│   │   ├── screen.py      # Base screen class
│   │   ├── screen_manager.py # Screen stack management
│   │   ├── home_screen.py # Grid view of Pokémon
│   │   ├── list_screen.py # List view of Pokémon
│   │   ├── detail_screen.py # Pokémon detail view
│   │   ├── settings_screen.py # Settings menu
│   │   └── colors.py      # Retro color palette
│   ├── data/              # Data management and database
│   │   ├── database.py    # SQLite database operations
│   │   ├── loader.py      # PokéAPI data loader
│   │   ├── migrations.py  # Database migration system
│   │   └── manage_db.py   # CLI for database management
│   └── config.py          # Configuration settings (coming soon)
├── assets/                # Images, sprites, fonts
│   ├── sprites/           # Pokémon sprites
│   ├── icons/             # UI icons
│   └── fonts/             # Custom fonts
├── data/                  # Database files
│   └── pokedex.db         # SQLite database (created on init)
├── docs/                  # Documentation
│   ├── database_schema.md # Database schema documentation
│   ├── data_loading_guide.md # Guide for loading Pokémon data
│   ├── ui_guide.md        # UI system and screen documentation
│   ├── hardware_guide.md  # Hardware assembly instructions
│   ├── pi_installation_guide.md # Raspberry Pi setup guide
│   ├── pi_optimization_guide.md # Performance tuning guide
│   ├── api_usage.md       # API integration guide
│   └── troubleshooting.md # Common issues and solutions
├── tests/                 # Unit and integration tests
│   ├── __init__.py
│   ├── test_database.py   # Database module tests
│   ├── test_input_manager.py # Input manager tests
│   ├── test_performance_monitor.py # Performance monitoring tests
│   └── test_*.py          # Additional test modules
├── tools/                 # Performance and testing tools
│   ├── profile_performance.py # Performance profiling tool
│   ├── test_input_latency.py # Input latency tester
│   └── README.md          # Tools documentation
├── demos/                 # Visual demonstration scripts
│   ├── demo_screenshot.py # Generate reference screenshots
│   ├── demo_evolution_display.py # Evolution panel testing
│   ├── demo_tab_system.py # Tab navigation demo
│   └── demo_*.py          # Additional visual demos
├── examples/              # Example scripts
│   ├── database_usage.py  # Database usage examples
│   ├── config_example.py  # Configuration example
│   └── ui_demo.py         # UI demo (no database needed)
├── .gitignore            # Git ignore rules
├── LICENSE               # MIT License with IP disclaimer
├── README.md             # This file
└── requirements.txt      # Python dependencies
```

## 🔧 Development

### Database Setup

ShokeDex uses SQLite to store Pokémon data locally. Set up the database:

```bash
# Initialize the database schema
python src/data/manage_db.py init

# Load Gen 1-3 Pokémon data from PokéAPI (takes 10-20 minutes)
python src/data/manage_db.py seed --gen 1-3

# Or load individual generations
python src/data/manage_db.py seed --gen 1  # Gen 1 only
python src/data/manage_db.py seed --gen 2  # Gen 2 only
python src/data/manage_db.py seed --gen 3  # Gen 3 only

# Check database statistics
python src/data/manage_db.py stats

# Query a specific Pokémon
python src/data/manage_db.py query --id 25
python src/data/manage_db.py query --name pikachu
```

**Note:** Loading data requires an internet connection to access PokéAPI. See [docs/data_loading_guide.md](docs/data_loading_guide.md) for detailed instructions.

### Sprite Processing

ShokeDex includes a sprite processing pipeline that converts Pokémon sprites to a Gameboy Color palette:

```bash
# Process all generations (1-3)
python src/data/sprite_processor.py --all

# Process a specific generation
python src/data/sprite_processor.py --gen 1

# Process a specific Pokémon
python src/data/sprite_processor.py --pokemon 25  # Pikachu
```

Processed sprites are saved in `assets/sprites/thumb/` (32x32) and `assets/sprites/detail/` (96x96). See [docs/sprite_pipeline.md](docs/sprite_pipeline.md) for detailed documentation.

### Running the Application

```bash
# Activate virtual environment
source venv/bin/activate

# Run the main application (requires database)
python src/main.py

# Or run the UI demo without database
python examples/ui_demo.py
```

The application features:
- **Grid View**: Browse Pokémon in a 4x3 grid
- **Detail View**: View Pokémon stats, types, and information
- **Settings**: Configure input mode and other options
- **Keyboard Controls**: Arrow keys to navigate, Enter to select, ESC to go back

See [docs/ui_guide.md](docs/ui_guide.md) for complete UI documentation.

### Running Tests

```bash
# Run all tests
python -m unittest discover tests -v

# Run specific test module
python -m unittest tests.test_database -v
```

### Visual Demonstrations

Demo scripts for visual testing and reference screenshots:

```bash
# Generate reference screenshots for all features
python demos/demo_screenshot.py

# Test evolution panel rendering
python demos/demo_evolution_display.py

# Test tab navigation system
python demos/demo_tab_system.py
```

Screenshots are saved to `screenshots/` directory. See individual demo scripts for detailed usage.

### Performance Profiling and Optimization

ShokeDex includes tools for profiling and optimizing performance on Raspberry Pi:

```bash
# Profile application performance (runs for 60 seconds)
python tools/profile_performance.py 60

# Test button input latency
python tools/test_input_latency.py keyboard 10  # Development
python tools/test_input_latency.py gpio 10      # On Raspberry Pi

# View detailed tool documentation
cat tools/README.md
```

**Performance Documentation:**
- [Raspberry Pi Installation Guide](docs/pi_installation_guide.md) - Complete setup instructions
- [Performance Optimization Guide](docs/pi_optimization_guide.md) - Tuning tips and best practices
- [Hardware Assembly Guide](docs/hardware_guide.md) - GPIO wiring and button setup
- [Tools README](tools/README.md) - Profiling and testing tools

**Target Performance:**
- **Raspberry Pi 3B+**: 30 FPS, <80% CPU, <150MB RAM, <50ms input latency
- **Raspberry Pi 4**: 60 FPS, <60% CPU, <200MB RAM, <30ms input latency

### Code Style

This project follows PEP 8 guidelines. Consider using:
- `black` for code formatting
- `pylint` or `flake8` for linting
- `mypy` for type checking

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Intellectual Property Notice

This is a fan-made project inspired by the Pokémon franchise. Pokémon and all related content are trademarks of Nintendo, Creatures Inc., and GAME FREAK Inc. This project is not affiliated with or endorsed by these companies and is intended for educational and personal use only.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, fork the repository, and create pull requests.

## 📞 Contact

For questions or suggestions, please open an issue on GitHub.

---

**Happy Pokédex Building!** 🎮✨
