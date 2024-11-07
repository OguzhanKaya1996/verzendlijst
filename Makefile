# Makefile for compiling Python script into a standalone macOS application

# Variables
SCRIPT_NAME := app.py
APP_NAME := BolSplines
ICON_FILE := path/to/your/icon.icns  # Optional: specify path to .icns icon file
VENV_DIR := venv
REQUIREMENTS := requirements.txt

# Detect operating system
OS := $(shell uname)

# Default target
all: check setup build

# Check target - Verifies Python is installed
check:
	@echo "Checking for Python installation..."
	@python3 --version || (echo "Python 3 is not installed. Please install Python 3." && exit 1)

# Setup target - Creates a virtual environment and installs dependencies
setup: check
	@echo "Creating virtual environment in $(VENV_DIR)..."
	python3 -m venv $(VENV_DIR)
	@echo "Virtual environment created. Installing dependencies..."
	$(VENV_DIR)/bin/pip install --upgrade pip
	$(VENV_DIR)/bin/pip install pyinstaller
	$(VENV_DIR)/bin/pip install -r $(REQUIREMENTS)
	@echo "Dependencies and PyInstaller installed."

# Build target - Compiles the script into a standalone application based on OS
build: setup
ifeq ($(OS), Darwin)
	@echo "Building macOS application..."
	$(VENV_DIR)/bin/pyinstaller --onefile --windowed --name $(APP_NAME) $(SCRIPT_NAME) $(ICON_OPTION)
else ifeq ($(OS), Linux)
	@echo "Building Linux application..."
	$(VENV_DIR)/bin/pyinstaller --onefile --name $(APP_NAME) $(SCRIPT_NAME)
else
	@echo "Building Windows application..."
	$(VENV_DIR)/Scripts/pyinstaller --onefile --name $(APP_NAME).exe $(SCRIPT_NAME)
endif
	@echo "Build completed. The application is located in the 'dist' directory."

# Clean target - Removes virtual environment and build artifacts
clean:
	@echo "Cleaning up virtual environment and build artifacts..."
	rm -rf $(VENV_DIR) build dist __pycache__ $(APP_NAME).spec
	@echo "Cleanup completed."

# Icon option
ifeq ($(OS), Darwin)
ICON_OPTION := --icon=$(ICON_FILE)
else
ICON_OPTION :=
endif
