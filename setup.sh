#!/bin/bash

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

echo "Setup complete! Don't forget to configure your credentials in the .env file before running the application."