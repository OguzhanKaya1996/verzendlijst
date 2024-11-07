# Makefile for compiling Python script into a standalone macOS application

# Variables
SCRIPT_NAME := app.py
APP_NAME := TensorNetworkBolSplines
VENV_DIR := venv
REQUIREMENTS := requirements.txt

# Detect operating system
OS := $(shell uname -s)

# Define paths for pip and pyinstaller based on OS
ifeq ($(OS), Windows_NT)
    PYTHON := python
    PIP := $(VENV_DIR)/Scripts/pip
    PYINSTALLER := $(VENV_DIR)/Scripts/pyinstaller
else
    PYTHON := python3
    PIP := $(VENV_DIR)/bin/pip
    PYINSTALLER := $(VENV_DIR)/bin/pyinstaller
endif

# Default target
all: check setup build

# Check target - Verifies Python is installed
check:
	@echo "Checking for Python installation..."
	@$(PYTHON) --version || (echo "Python 3 is not installed. Please install Python 3." && exit 1)

# Setup target - Creates a virtual environment and installs dependencies
setup: check
	@echo "Creating virtual environment in $(VENV_DIR)..."
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "Virtual environment created. Installing dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install -r $(REQUIREMENTS)
	$(PIP) install pyinstaller
	@echo "Dependencies and PyInstaller installed."

# Build target - Compiles the script into a standalone application based on OS
build: setup
ifeq ($(OS), Darwin)
	@echo "Building macOS application..."
	$(PYINSTALLER) --onefile --windowed --name $(APP_NAME) $(SCRIPT_NAME) 
else ifeq ($(OS), Linux)
	@echo "Building Linux application..."
	$(PYINSTALLER) --onefile --name $(APP_NAME) $(SCRIPT_NAME)
else
	@echo "Building Windows application..."
	$(PYINSTALLER) --onefile --name $(APP_NAME).exe $(SCRIPT_NAME)
endif
	@echo "Build completed. The application is located in the 'dist' directory."

# Clean target - Removes virtual environment and build artifacts
clean:
	@echo "Cleaning up virtual environment and build artifacts..."
	rm -rf $(VENV_DIR) build dist __pycache__ $(APP_NAME).spec
	@echo "Cleanup completed."

