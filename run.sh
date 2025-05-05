#!/bin/bash
# Run Script for Weekly Report Generator
#
# This script manages the Python virtual environment activation and deactivation,
# and executes the main application script for generating weekly reports.
#
# Authors:
#     - Calvert Tanudihardjo (calvert.tanudihardjo@gdplabs.id)

if [[ "$VIRTUAL_ENV" == "" ]]; then
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        echo "Error: Virtual environment 'venv' not found. Please run the setup script first."
        exit 1
    fi
else
    echo "Virtual environment is already activated."
fi

python3 main.py

if [[ "$VIRTUAL_ENV" != "" && "$VIRTUAL_ENV" == *"/venv" ]]; then
    deactivate
fi

echo "Press Enter to close this window..."
read