# Installation Guide

This guide provides detailed installation instructions for ChatGPT Browser across different operating systems and deployment scenarios.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Prerequisites](#prerequisites)
3. [Installation Methods](#installation-methods)
4. [Operating System Specific Instructions](#operating-system-specific-instructions)
5. [Development Setup](#development-setup)
6. [Production Deployment](#production-deployment)
7. [Docker Deployment](#docker-deployment)
8. [Troubleshooting](#troubleshooting)

## System Requirements

### Minimum Requirements
- **CPU**: 1 GHz dual-core processor
- **RAM**: 2 GB
- **Storage**: 1 GB free disk space
- **Network**: Internet connection for initial setup

### Recommended Requirements
- **CPU**: 2 GHz quad-core processor or better
- **RAM**: 4 GB or more
- **Storage**: 5 GB free disk space (for large conversation databases)
- **Network**: Stable internet connection

### Supported Operating Systems
- **Windows**: 10 (version 1903+) / 11
- **macOS**: 10.15 (Catalina) or later
- **Linux**: Ubuntu 18.04+, CentOS 7+, Debian 9+

## Prerequisites

### Python Installation

#### Windows
1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer with "Add Python to PATH" checked
3. Verify installation:
   ```cmd
   python --version
   pip --version
   ```

#### macOS
```bash
# Using Homebrew (recommended)
brew install python

# Or download from python.org
# Verify installation
python3 --version
pip3 --version
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Verify installation
python3 --version
pip3 --version
```

#### Linux (CentOS/RHEL)
```bash
sudo yum install python3 python3-pip

# Or for newer versions
sudo dnf install python3 python3-pip

# Verify installation
python3 --version
pip3 --version
```

### Git Installation

#### Windows
Download and install from [git-scm.com](https://git-scm.com/download/win)

#### macOS
```bash
# Using Homebrew
brew install git

# Or using Xcode Command Line Tools
xcode-select --install
```

#### Linux
```bash
# Ubuntu/Debian
sudo apt install git

# CentOS/RHEL
sudo yum install git
```

## Installation Methods

### Method 1: Standard Installation (Recommended)

#### Step 1: Clone the Repository
```bash
git clone https://github.com/actuallyrizzn/chatGPT-browser.git
cd chatGPT-browser
```

#### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

#### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 4: Initialize Database
```bash
python init_db.py
```

#### Step 5: Start the Application
```bash
python app.py
```

### Method 2: Development Installation

For developers who want to contribute to the project:

```bash
# Clone with submodules
git clone --recursive https://github.com/actuallyrizzn/chatGPT-browser.git
cd chatGPT-browser

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available

# Install pre-commit hooks
pre-commit install

# Initialize database
python init_db.py

# Run tests
python -m pytest

# Start in development mode
export FLASK_ENV=development
export FLASK_DEBUG=1
python app.py
```

## Operating System Specific Instructions

### Windows Installation

#### Using PowerShell
```powershell
# Enable script execution (if needed)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Clone repository
git clone https://github.com/actuallyrizzn/chatGPT-browser.git
cd chatGPT-Browser\chatGPT-browser

# Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py

# Start application
python app.py
```

#### Using Command Prompt
```cmd
# Clone repository
git clone https://github.com/actuallyrizzn/chatGPT-browser.git
cd chatGPT-Browser\chatGPT-browser

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py

# Start application
python app.py
```

### macOS Installation

#### Using Terminal
```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python and Git
brew install python git

# Clone repository
git clone https://github.com/actuallyrizzn/chatGPT-browser.git
cd chatGPT-Browser/chatGPT-browser

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py

# Start application
python app.py
```

### Linux Installation

#### Ubuntu/Debian
```bash
# Update package list
sudo apt update

# Install dependencies
sudo apt install python3 python3-pip python3-venv git

# Clone repository
git clone https://github.com/actuallyrizzn/chatGPT-browser.git
cd chatGPT-Browser/chatGPT-browser

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py

# Start application
python app.py
```

#### CentOS/RHEL/Fedora
```bash
# Install dependencies
sudo dnf install python3 python3-pip git  # For Fedora/RHEL 8+
# OR
sudo yum install python3 python3-pip git  # For older versions

# Clone repository
git clone https://github.com/actuallyrizzn/chatGPT-browser.git
cd chatGPT-Browser/chatGPT-browser

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py

# Start application
python app.py
```

## Development Setup

### Setting Up Development Environment

1. **Fork the Repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/actuallyrizzn/chatGPT-browser.git
   cd chatGPT-browser
   ```

2. **Add Upstream Remote**
   ```bash
   git remote add upstream https://github.com/actuallyrizzn/chatGPT-browser.git
   ```

3. **Create Development Branch**
   ```bash
   git checkout -b development
   ```

4. **Install Development Dependencies**
   ```bash
   cd chatGPT-browser
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   pip install pytest pytest-cov black flake8 mypy
   ```

5. **Set Up Pre-commit Hooks**
   ```bash
   pip install pre-commit
   pre-commit install
   ```

6. **Configure Environment Variables**
   ```bash
   # Create .env file
   cat > .env << EOF
   FLASK_ENV=development
   FLASK_DEBUG=True
   DATABASE_PATH=./chatgpt.db
   SECRET_KEY=dev-secret-key-change-in-production
   EOF
   ```

### Running Tests
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=app

# Run specific test file
python -m pytest tests/test_app.py

# Run with verbose output
python -m pytest -v
```

### Code Quality Checks
```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .

# Run all checks
pre-commit run --all-files
```

## Production Deployment

### Using Gunicorn (Linux/macOS)

1. **Install Gunicorn**
   ```bash
   pip install gunicorn
   ```

2. **Create WSGI Entry Point**
   ```python
   # wsgi.py
   from app import app
   
   if __name__ == "__main__":
       app.run()
   ```

3. **Create Gunicorn Configuration**
   ```python
   # gunicorn.conf.py
   bind = "0.0.0.0:8000"
   workers = 4
   worker_class = "sync"
   worker_connections = 1000
   max_requests = 1000
   max_requests_jitter = 100
   timeout = 30
   keepalive = 2
   ```

4. **Start with Gunicorn**
   ```bash
   gunicorn -c gunicorn.conf.py wsgi:app
   ```

### Using Waitress (Windows)

1. **Install Waitress**
   ```bash
   pip install waitress
   ```

2. **Create Production Entry Point**
   ```python
   # run_production.py
   from waitress import serve
   from app import app
   
   if __name__ == "__main__":
       serve(app, host="0.0.0.0", port=8000)
   ```

3. **Start with Waitress**
   ```bash
   python run_production.py
   ```

### Using Systemd (Linux)

1. **Create Service File**
   ```ini
   # /etc/systemd/system/chatgpt-browser.service
   [Unit]
   Description=ChatGPT Browser
   After=network.target
   
   [Service]
   Type=simple
   User=chatgpt-browser
   WorkingDirectory=/opt/chatgpt-browser
   Environment=PATH=/opt/chatgpt-browser/.venv/bin
   ExecStart=/opt/chatgpt-browser/.venv/bin/gunicorn -c gunicorn.conf.py wsgi:app
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

2. **Enable and Start Service**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable chatgpt-browser
   sudo systemctl start chatgpt-browser
   ```

## Docker Deployment

### Using Docker Compose

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   EXPOSE 8000
   
   CMD ["gunicorn", "--bind", "0.0.0.0:8000", "wsgi:app"]
   ```

2. **Create docker-compose.yml**
   ```yaml
   version: '3.8'
   
   services:
     chatgpt-browser:
       build: .
       ports:
         - "8000:8000"
       volumes:
         - ./data:/app/data
       environment:
         - FLASK_ENV=production
         - DATABASE_PATH=/app/data/chatgpt.db
       restart: unless-stopped
   ```

3. **Build and Run**
   ```bash
   docker-compose up -d
   ```

### Using Docker Run

```bash
# Build image
docker build -t chatgpt-browser .

# Run container
docker run -d \
  --name chatgpt-browser \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -e FLASK_ENV=production \
  chatgpt-browser
```

## Troubleshooting

### Common Installation Issues

#### Python Version Issues
**Problem**: "Python version not supported"
**Solution**:
```bash
# Check Python version
python --version

# Install correct version
# Windows: Download from python.org
# macOS: brew install python@3.11
# Linux: sudo apt install python3.11
```

#### Virtual Environment Issues
**Problem**: "venv module not found"
**Solution**:
```bash
# Install venv module
# Ubuntu/Debian
sudo apt install python3-venv

# CentOS/RHEL
sudo yum install python3-venv

# macOS
brew install python3
```

#### Permission Issues
**Problem**: "Permission denied" errors
**Solution**:
```bash
# Fix directory permissions
sudo chown -R $USER:$USER /path/to/project

# Fix virtual environment permissions
chmod +x .venv/bin/activate
```

#### Port Already in Use
**Problem**: "Address already in use"
**Solution**:
```bash
# Find process using port
lsof -i :5000

# Kill process
kill -9 <PID>

# Or use different port
python app.py --port 5001
```

#### Database Issues
**Problem**: "Database locked" or "Permission denied"
**Solution**:
```bash
# Check file permissions
ls -la chatgpt.db

# Fix permissions
chmod 644 chatgpt.db

# Reinitialize database
python init_db.py
```

### Performance Issues

#### Slow Import
**Problem**: Large files take too long to import
**Solution**:
- Split large export files
- Increase system RAM
- Use SSD storage
- Close other applications

#### High Memory Usage
**Problem**: Application uses too much memory
**Solution**:
- Use Nice Mode instead of Dev Mode
- Limit concurrent imports
- Increase swap space
- Restart application periodically

### Network Issues

#### Can't Access Application
**Problem**: "Connection refused" or "Page not found"
**Solution**:
```bash
# Check if application is running
ps aux | grep python

# Check port binding
netstat -tlnp | grep 5000

# Check firewall settings
sudo ufw status
```

#### External Access Issues
**Problem**: Can't access from other devices
**Solution**:
```bash
# Bind to all interfaces
python app.py --host 0.0.0.0

# Configure firewall
sudo ufw allow 5000

# Check network configuration
ip addr show
```

### Getting Help

If you encounter issues not covered in this guide:

1. **Check the logs**:
   ```bash
   # Application logs
   tail -f app.log

   # System logs
   journalctl -u chatgpt-browser -f
   ```

2. **Enable debug mode**:
   ```bash
   export FLASK_DEBUG=1
   python app.py
   ```

3. **Search existing issues** on GitHub

4. **Create a new issue** with:
   - Operating system and version
   - Python version
   - Error message and stack trace
   - Steps to reproduce

---

For additional help, see the [main README](../README.md) or [API Reference](./API_REFERENCE.md). 