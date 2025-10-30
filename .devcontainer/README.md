# ShokeDex Development Container

This directory contains the configuration for GitHub Codespaces and Visual Studio Code Dev Containers to provide a consistent, fully-configured development environment for ShokeDex.

## 🚀 Getting Started

### Using GitHub Codespaces

1. Navigate to the ShokeDex repository on GitHub
2. Click the green "Code" button
3. Select the "Codespaces" tab
4. Click "Create codespace on [branch]"
5. Wait for the container to build and initialize (first time: ~3-5 minutes)
6. Start coding!

### Using VS Code Dev Containers (Local)

**Prerequisites:**
- Docker Desktop installed and running
- Visual Studio Code with the "Dev Containers" extension

**Steps:**
1. Open the ShokeDex repository in VS Code
2. Press `F1` or `Ctrl+Shift+P` (Windows/Linux) / `Cmd+Shift+P` (Mac)
3. Type "Dev Containers: Reopen in Container" and select it
4. Wait for the container to build and initialize
5. Start coding!

## 🛠️ What's Included

### Base Image
- **Python 3.11** (Debian Bullseye-based)
- Git and GitHub CLI pre-installed

### Python Dependencies
Automatically installed from `requirements.txt`:
- pygame (2.5.0+) - Graphics rendering and display management
- Pillow (10.0.0+) - Image processing
- gpiozero (2.0.0+) - GPIO interface (mock mode in container)
- requests (2.31.0+) - HTTP client for API calls

### Development Tools
- **black** - Code formatting
- **pylint** - Code linting
- **flake8** - Style checking
- **mypy** - Type checking
- **pytest** - Testing framework

### VS Code Extensions
Automatically installed:
- Python extension pack
- Pylance (language server)
- Black formatter
- Pylint
- Python debugger
- Auto-docstring generator
- IntelliCode
- GitLens
- GitHub Copilot (if you have access)

### System Libraries
- SDL2 libraries for pygame support
- Image processing libraries
- Development headers

## 📋 Post-Creation Setup

The container automatically runs `postCreate.sh` which:
1. Upgrades pip
2. Installs Python dependencies
3. Installs development tools
4. Installs system dependencies for pygame
5. Creates the data directory
6. Initializes the database schema
7. Runs tests to verify the setup

## 🎯 Development Workflow

### Database Operations

```bash
# Initialize database schema
python src/data/manage_db.py init

# Seed with Pokémon data (requires internet)
python src/data/manage_db.py seed --gen 1-3

# Query a specific Pokémon
python src/data/manage_db.py query --id 25
python src/data/manage_db.py query --name pikachu

# View database statistics
python src/data/manage_db.py stats
```

### Running Tests

```bash
# Run all tests
python -m unittest discover tests -v

# Run specific test module
python -m unittest tests.test_database -v

# Using pytest (if you prefer)
pytest tests/ -v
```

### Code Quality

```bash
# Format code with black
black src/ tests/

# Lint code with pylint
pylint src/

# Check code style with flake8
flake8 src/ tests/

# Type checking with mypy
mypy src/
```

### Running Examples

```bash
# Run database usage examples
python examples/database_usage.py
```

## 🔧 Configuration Files

- **devcontainer.json** - Main configuration file
  - Defines the base image
  - Configures VS Code settings and extensions
  - Sets up environment variables
  - Defines post-create commands

- **postCreate.sh** - Setup script
  - Runs after container creation
  - Installs dependencies
  - Initializes the project

## 🌐 Environment Variables

The following environment variables are automatically set:
- `PYTHONPATH=/workspaces/ShokeDex` - Ensures Python can find project modules
- `DISPLAY=:0` - For potential GUI applications

## 📝 VS Code Settings

Pre-configured settings:
- Python interpreter: `/usr/local/bin/python`
- Linting: Enabled with pylint
- Formatting: Black (format on save enabled)
- Testing: unittest framework
- Line rulers at 79 and 120 characters (PEP 8 compliance)
- Auto-trim trailing whitespace
- Auto-insert final newline

## 🔍 Troubleshooting

### Database Issues

If the database fails to initialize:
```bash
# Remove existing database
rm data/pokedex.db

# Re-initialize
python src/data/manage_db.py init
```

### Dependency Issues

If dependencies fail to install:
```bash
# Reinstall dependencies
pip install --upgrade --force-reinstall -r requirements.txt
```

### pygame Issues

pygame may not display graphics in a container without a display server. For development:
- Database operations work normally
- Unit tests work normally
- Use the Raspberry Pi for testing actual display functionality

### Container Rebuild

If you need to rebuild the container from scratch:
1. Press `F1` or `Ctrl+Shift+P`
2. Type "Dev Containers: Rebuild Container"
3. Select it and wait for the rebuild

## 🚧 Limitations

- **GPIO Functionality**: Real GPIO operations require Raspberry Pi hardware. The container uses mock GPIO for development.
- **Display Testing**: Graphics rendering with pygame requires a display server. Test display features on actual Raspberry Pi hardware.
- **Performance**: Container performance depends on your host machine resources.

## 📚 Additional Resources

- [GitHub Codespaces Documentation](https://docs.github.com/en/codespaces)
- [VS Code Dev Containers Documentation](https://code.visualstudio.com/docs/devcontainers/containers)
- [ShokeDex Project README](../README.md)
- [Database Schema Documentation](../docs/database_schema.md)
- [Implementation Summary](../docs/IMPLEMENTATION_SUMMARY.md)

## 🤝 Contributing

When contributing to ShokeDex:
1. Use the dev container for a consistent environment
2. Run tests before committing: `python -m unittest discover tests -v`
3. Format code with black: `black src/ tests/`
4. Follow PEP 8 guidelines
5. Update documentation as needed

## 💡 Tips

- Use the integrated terminal in VS Code for running commands
- Leverage IntelliSense for code completion
- Use the Python debugger for troubleshooting
- The database is persisted in the `data/` directory
- Check `postCreate.sh` output in the terminal for setup issues

---

**Happy Pokédex Development!** 🎮✨
