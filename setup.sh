#!/bin/bash
# Setup Script for Weekly Report Generator
#
# This script automates the initial setup process including Python installation,
# virtual environment creation, dependency installation, and configuration file setup.
#
# Authors:
#     - Calvert Tanudihardjo (calvert.tanudihardjo@gdplabs.id)

# Exit immediately if a command exits with a non-zero status
set -e

# 1. Install Python (Ubuntu usually comes with Python, but we'll ensure it's installed)
echo "Updating package list and installing Python..."
sudo apt update
sudo apt install -y python3 python3-pip python3-venv

# 2. Install python venv (it's included with Python 3.3+, but we ensure it's installed)
sudo apt install -y python3-venv

# 3. Make python venv
echo "Creating virtual environment..."
python3 -m venv venv

# 4. Activate venv
echo "Activating virtual environment..."
source venv/bin/activate

# 5. Install from requirements.txt
echo "Installing requirements..."
pip install -r requirements.txt

# 6. Copy .env.example to .env
echo "Copying .env.example to .env..."
if [ -f .env.example ]; then
    cp .env.example .env
    echo ".env file created successfully."
else
    echo "Warning: .env.example file not found. Please create .env file manually."
fi

# 7. Create templates directory if it doesn't exist
echo "Setting up templates directory..."
mkdir -p templates

# 8. Copy template.example.md to templates/template.md
echo "Copying template.example.md to templates/template.md..."
if [ -f templates/template.example.md ]; then
    cp templates/template.example.md templates/template.md
    echo "template.md file created successfully."
else
    echo "Warning: templates/template.example.md file not found. Please create templates/template.md file manually."
fi

echo "Setup complete! Don't forget to configure your credentials in the .env file before running the application."

# Keep the terminal open
echo "Press Enter to close this window..."
read