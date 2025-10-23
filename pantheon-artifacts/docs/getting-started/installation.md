---
doc_id: getting-started-installation
title: Installation and System Requirements
description: Complete guide for installing the Pantheon Framework as a pip package including prerequisites, installation commands, virtual environment setup, and verification steps for the framework tool
keywords: [installation, pip install, python requirements, virtual environment, framework setup, system prerequisites, package manager, end-user, beginner]
relevance: Essential starting point for setting up the Pantheon Framework tool before project initialization and team configuration
---

# Installation and System Requirements

Pantheon is distributed as a standard Python package, installable via `pip`. This document covers the installation process and system requirements for the Pantheon Framework tool.

## Deployment Model: Pip-Installable Package

Pantheon follows a clean separation between the **Pantheon Framework (the tool)** and the **Team Packages (the user's data)**.

### The Tool

- The `pantheon` command-line interface and its underlying engine
- Installed into a Python environment (e.g., virtual environment)
- Stateless and can be used across multiple projects
- Updates managed through `pip install --upgrade pantheon-framework`

### The Data

- The `pantheon-teams/` directory containing user-defined agents, processes, and artifacts
- Resides directly within the user's project repository
- Owned, version-controlled, and modified by the user
- Contains the team's intellectual property—its processes

This separation ensures that the tool can evolve independently while the user retains complete ownership and history of their team's processes.

## System Prerequisites

Before installing Pantheon, ensure your system meets the following requirements:

### Required Software

- **Python 3.11 or higher**: Pantheon requires modern Python features and type annotations
- **pip package manager**: Standard Python package installer (included with Python)
- **Git**: For version control of team packages (recommended)

### Supported Platforms

- Linux (Ubuntu 20.04+, Debian 10+, CentOS 8+)
- macOS (10.15 Catalina or later)
- Windows (10 or later, with Windows Terminal recommended)

### System Resources

- **Disk Space**: Minimum 50MB for framework installation, additional space for team packages and artifacts
- **Memory**: Minimum 2GB RAM for typical operations
- **Network**: Internet connection required for initial installation and package updates

## Installation Methods

### Standard Installation

Install Pantheon directly into your system Python or current environment:

```bash
# Install from PyPI
pip install pantheon-framework

# Verify installation
pantheon --help
```

### Virtual Environment Installation (Recommended)

Using a virtual environment isolates Pantheon and its dependencies from other Python projects:

```bash
# Create a new virtual environment
python -m venv pantheon-env

# Activate the virtual environment
# On Linux/macOS:
source pantheon-env/bin/activate

# On Windows:
pantheon-env\Scripts\activate

# Install Pantheon in the virtual environment
pip install pantheon-framework

# Verify installation
pantheon --help
```

### Project-Specific Installation

Install Pantheon as a project dependency using `requirements.txt`:

```txt
# requirements.txt
pantheon-framework>=1.0.0
```

```bash
# Install all project dependencies including Pantheon
pip install -r requirements.txt
```

### Development Installation

For contributing to the Pantheon Framework itself:

```bash
# Clone the repository
git clone https://github.com/pantheon/pantheon-framework.git
cd pantheon-framework

# Install in editable mode with development dependencies
pip install -e ".[dev]"

# Run tests to verify installation
pytest
```

## Installation Verification

After installation, verify that Pantheon is correctly installed and accessible:

### Check Version

```bash
pantheon --version
```

Expected output:
```
Pantheon Framework v1.0.0
```

### Check Command Availability

```bash
pantheon --help
```

Expected output should display the main command groups:
```
Usage: pantheon [OPTIONS] COMMAND [ARGS]...

  Pantheon Framework - AI Team Orchestration

Commands:
  init     Initialize project or switch active team
  get      Retrieve information (process, schema, sections, tempfile)
  execute  Execute a process
  set      Update framework data (team-data)
```

### Check Python Version

```bash
python --version
```

Expected output:
```
Python 3.11.0 or higher
```

### Check pip Installation

```bash
pip show pantheon-framework
```

Expected output should display package information:
```
Name: pantheon-framework
Version: 1.0.0
Location: /path/to/site-packages
Requires: jinja2, jsonschema, pyyaml, ...
```

## Updating Pantheon

Keep your Pantheon installation up to date to access the latest features and bug fixes:

### Standard Update

```bash
# Update to latest version
pip install --upgrade pantheon-framework

# Verify new version
pantheon --version
```

### Update to Specific Version

```bash
# Install specific version
pip install pantheon-framework==1.2.0
```

### Check for Updates

```bash
# List outdated packages
pip list --outdated | grep pantheon-framework
```

## Uninstallation

If you need to remove Pantheon from your system:

```bash
# Uninstall Pantheon
pip uninstall pantheon-framework

# Confirm removal
pantheon --help  # Should return "command not found"
```

**Note:** Uninstalling the framework does not remove your project's team packages or generated artifacts. These remain in your project directory.

## Common Installation Issues

### Python Version Mismatch

**Problem:** `pantheon-framework requires Python >=3.11`

**Solution:**
```bash
# Check current Python version
python --version

# Install Python 3.11+ from python.org or your package manager
# On Ubuntu:
sudo apt install python3.11

# On macOS with Homebrew:
brew install python@3.11
```

### pip Not Found

**Problem:** `pip: command not found`

**Solution:**
```bash
# Install pip
python -m ensurepip --upgrade

# Or on Ubuntu:
sudo apt install python3-pip
```

### Permission Errors

**Problem:** `Permission denied` when installing

**Solution:**
```bash
# Option 1: Use user installation (recommended)
pip install --user pantheon-framework

# Option 2: Use virtual environment (best practice)
python -m venv pantheon-env
source pantheon-env/bin/activate
pip install pantheon-framework
```

### Network/Proxy Issues

**Problem:** Cannot connect to PyPI

**Solution:**
```bash
# Use proxy settings
pip install --proxy http://proxy.server:port pantheon-framework

# Or configure pip permanently
pip config set global.proxy http://proxy.server:port
```

### Conflicting Dependencies

**Problem:** `Cannot install due to conflicting dependencies`

**Solution:**
```bash
# Use virtual environment to isolate dependencies
python -m venv clean-env
source clean-env/bin/activate
pip install pantheon-framework
```

## Environment Configuration

### PATH Configuration

Ensure the Python scripts directory is in your PATH:

**Linux/macOS:**
```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="$HOME/.local/bin:$PATH"
```

**Windows:**
```powershell
# Add Python Scripts directory to PATH via System Properties
# Typically: C:\Users\<username>\AppData\Local\Programs\Python\Python311\Scripts
```

### Shell Completion (Optional)

Enable command completion for your shell:

```bash
# Bash
pantheon --install-completion bash

# Zsh
pantheon --install-completion zsh

# Fish
pantheon --install-completion fish
```

## Post-Installation Next Steps

After successful installation:

1. **Initialize a project**: See initialization guide for `pantheon init` workflow
2. **Configure team**: Select or create a team package for your project
3. **Verify team agents**: Ensure agent definitions are properly installed
4. **Test basic commands**: Run `pantheon get team-data --actor pantheon` to verify functionality

## Troubleshooting Resources

### Check Installation Location

```bash
# Find where pantheon is installed
which pantheon  # Linux/macOS
where pantheon  # Windows

# Check Python package location
python -c "import pantheon; print(pantheon.__file__)"
```

### Validate Framework Files

```bash
# Verify bundled templates exist
python -c "import pantheon; import os; print(os.path.exists(os.path.join(os.path.dirname(pantheon.__file__), '_templates')))"
```

### Enable Debug Logging

```bash
# Set environment variable for verbose output
export PANTHEON_DEBUG=1
pantheon --help
```

For additional support, consult the framework documentation or file an issue on the project repository.
