#!/bin/bash

# Check if virtual environment is already activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    # Virtual environment is not activated, so activate it
    if [ -d "venv" ]; then
        echo "Activating virtual environment..."
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
    echo "Deactivating virtual environment..."
    deactivate
fi