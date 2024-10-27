#!/bin/bash
# Run Script for Weekly Report Generator
#
# This script manages the Python virtual environment activation and deactivation,
# and executes the main application script for generating weekly reports.
#
# Authors:
#     - Calvert Tanudihardjo (calvert.tanudihardjo@gdplabs.id)

# Check if virtual environment is already activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    # Virtual environment is not activated, so activate it
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        echo "Error: Virtual environment 'venv' not found. Please run the setup script first."
        exit 1
    fi
else
    echo "Virtual environment is already activated."
fi

# Run the main Python script
python3 main.py

# Deactivate the virtual environment when the script finishes
# Only deactivate if we activated it in this script
if [[ "$VIRTUAL_ENV" != "" && "$VIRTUAL_ENV" == *"/venv" ]]; then
    deactivate
fi

# Keep the terminal open
echo "Press Enter to close this window..."
read