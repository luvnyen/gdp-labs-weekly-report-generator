#!/bin/bash
# Setup Script for Weekly Report Generator
#
# This script automates the initial setup process including Python installation,
# virtual environment creation, dependency installation, and configuration file setup.
#
# Authors:
#     - Calvert Tanudihardjo (calvert.tanudihardjo@gdplabs.id)
#     - Sandy Akbar Dewangga (sandy.a.dewangga@gdplabs.id)

set -e  # Exit on error

########################################
# OS Detection
########################################
detect_os() {
    local os_name="$(uname -s)"
    case "$os_name" in
        Linux*)     echo "Linux";;
        Darwin*)    echo "Mac";;
        CYGWIN*|MINGW*|MSYS*) echo "Windows";;
        *)          echo "UNKNOWN";;
    esac
}

########################################
# Dependency Installation
########################################
install_dependencies_linux() {
    local packages=()
    if ! command -v python3 &> /dev/null; then packages+=(python3); fi
    if ! command -v pip3 &> /dev/null; then packages+=(python3-pip); fi
    if ! python3 -m venv --help &> /dev/null; then packages+=(python3-venv); fi
    if [ ${#packages[@]} -ne 0 ]; then
        echo "Installing missing packages: ${packages[*]}"
        sudo apt update
        sudo apt install -y "${packages[@]}"
    else
        echo "All required Python dependencies are already installed."
    fi
}

install_dependencies_mac() {
    if ! command -v python3 &> /dev/null; then
        echo "Python3 not found. Installing Python3 via Homebrew..."
        if ! command -v brew &> /dev/null; then
            echo "Homebrew not found. Installing Homebrew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
        brew install python3
    else
        echo "Python3 is already installed."
    fi
}

print_windows_instructions() {
    echo "This setup script is intended for Unix-like systems (Linux/macOS)."
    echo "For Windows, please install Python 3, pip, and virtualenv manually."
    echo "Then, run the following commands in your terminal:"
    echo "  python -m venv venv"
    echo "  venv\\Scripts\\activate (or source venv/bin/activate if using Git Bash)"
    echo "  pip install -r requirements.txt"
    echo "  cp .env.example .env"
    echo "  mkdir -p templates"
    echo "  cp templates/template.example.md templates/template.md"
}

########################################
# Virtual Environment Setup
########################################
setup_venv() {
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    else
        echo "Virtual environment already exists."
    fi
    echo "Activating virtual environment..."
    # shellcheck disable=SC1091
    source venv/bin/activate
}

########################################
# File and Directory Setup
########################################
setup_files_and_dirs() {
    echo "Installing requirements..."
    pip install -r requirements.txt

    echo "Copying .env.example to .env..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo ".env file created successfully."
    else
        echo "Warning: .env.example file not found. Please create .env file manually."
    fi

    echo "Setting up templates directory..."
    mkdir -p templates

    echo "Copying template.example.md to templates/template.md..."
    if [ -f templates/template.example.md ]; then
        cp templates/template.example.md templates/template.md
        echo "template.md file created successfully."
    else
        echo "Warning: templates/template.example.md file not found. Please create templates/template.md file manually."
    fi
}

########################################
# Main Script Logic
########################################
main() {
    local machine
    machine=$(detect_os)
    echo "Detected OS: $machine"

    case "$machine" in
        Linux)
            install_dependencies_linux
            setup_venv
            setup_files_and_dirs
            ;;
        Mac)
            install_dependencies_mac
            setup_venv
            setup_files_and_dirs
            ;;
        Windows)
            print_windows_instructions
            exit 1
            ;;
        *)
            echo "Unsupported OS: $machine"
            exit 1
            ;;
    esac

    echo "Setup complete! Don't forget to configure your credentials in the .env file before running the application."
    echo "Press Enter to close this window..."
    read
}

main "$@"