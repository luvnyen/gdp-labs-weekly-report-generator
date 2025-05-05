#!/bin/bash
# Google Docs Weekly Report Updater Script
#
# This script uploads the latest weekly report markdown content
# to the linked Google Docs document specified in an email.
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

python3 sync_to_google_docs.py

exit_code=$?

if [[ "$VIRTUAL_ENV" != "" && "$VIRTUAL_ENV" == *"/venv" ]]; then
    deactivate
fi

echo "Press Enter to close this window..."
read

exit $exit_code