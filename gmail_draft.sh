#!/bin/bash
# Gmail Draft Creator Script
#
# This script creates a Gmail draft from the most recent weekly report markdown file
# without generating a new report.
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

# Run the Gmail draft creator script
python3 create_gmail_draft.py

# Capture the exit code
exit_code=$?

# Deactivate the virtual environment when the script finishes
# Only deactivate if we activated it in this script
if [[ "$VIRTUAL_ENV" != "" && "$VIRTUAL_ENV" == *"/venv" ]]; then
    deactivate
fi

# Keep the terminal open
echo "Press Enter to close this window..."
read

# Return the exit code from the Python script
exit $exit_code