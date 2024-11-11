# Minimum CMake version
cmake_minimum_required(VERSION 3.14)

# Project name and version
project(TensorNetworkBolSplines VERSION 1.0)

# Find Python (adjust the required version as necessary)
find_package(Python3 COMPONENTS Interpreter REQUIRED)

# Add custom command to set up a virtual environment and install requirements
add_custom_target(venv
    COMMAND ${Python3_EXECUTABLE} -m venv venv
    COMMAND venv/bin/python3 -m pip install --upgrade pip
    COMMAND venv/bin/python3 -m pip install -r requirements.txt
    COMMENT "Setting up virtual environment and installing dependencies"
)

# Add custom command to run PyInstaller and package the application
add_custom_target(build-app ALL
    DEPENDS venv
    COMMAND venv/bin/python3 -m PyInstaller --onefile --name TensorNetworkBolSplines app.py
    COMMENT "Packaging application with PyInstaller"
)

# Clean up build artifacts
add_custom_target(clean-venv
    COMMAND ${CMAKE_COMMAND} -E remove_directory venv
    COMMAND ${CMAKE_COMMAND} -E remove_directory build
    COMMAND ${CMAKE_COMMAND} -E remove_directory dist
    COMMAND ${CMAKE_COMMAND} -E remove TensorNetworkBolSplines.spec
    COMMENT "Cleaning up virtual environment and build artifacts"
)
