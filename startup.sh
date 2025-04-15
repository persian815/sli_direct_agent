#!/bin/bash

# Exit on error
set -e

# Function for logging
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Function for error handling
handle_error() {
  log "ERROR: $1"
  # Continue execution despite errors
  return 0
}

# Set environment variables
WEBAPP_NAME="slifit"
RESOURCE_GROUP="slihackathon-2025-team2-rg"
APP_DIR="/home/site/wwwroot"
VENV_DIR="$APP_DIR/venv"
LOG_FILE="$APP_DIR/startup.log"

# Redirect output to log file
exec 1> >(tee -a "$LOG_FILE")
exec 2> >(tee -a "$LOG_FILE" >&2)

log "Starting application deployment process..."

# Print current directory
log "Current directory: $(pwd)"

# List directory contents
log "Directory contents:"
ls -la
log "Total files: $(ls -la | wc -l)"

# Create wwwroot directory if it doesn't exist
if [ ! -d "$APP_DIR" ]; then
  log "Creating wwwroot directory..."
  mkdir -p "$APP_DIR" || handle_error "Failed to create wwwroot directory"
fi

# Copy files from current directory to wwwroot if not already there
if [ "$(pwd)" != "$APP_DIR" ]; then
  log "Copying files to $APP_DIR..."
  cp -rv * "$APP_DIR/" 2>/dev/null || handle_error "Some files could not be copied"
fi

# Change to wwwroot directory
cd "$APP_DIR" || handle_error "Failed to change to wwwroot directory"
log "Changed to directory: $(pwd)"

# Check if startup.sh exists and set execute permissions
if [ -f "startup.sh" ]; then
  log "Found startup.sh, setting execute permissions..."
  chmod +x startup.sh || handle_error "Failed to set execute permissions on startup.sh"
fi

# Check for available Python versions
log "Checking for available Python versions..."
if command -v python3 &> /dev/null; then
  PYTHON_PATH="python3"
  log "Using Python 3: $($PYTHON_PATH --version 2>&1)"
elif command -v python &> /dev/null; then
  PYTHON_PATH="python"
  log "Using default Python: $($PYTHON_PATH --version 2>&1)"
else
  log "No Python found. Installing Python 3.9..."
  apt-get update || handle_error "Failed to update apt"
  apt-get install -y python3.9 python3.9-venv || handle_error "Failed to install Python 3.9"
  PYTHON_PATH="python3.9"
  log "Using Python 3.9: $($PYTHON_PATH --version 2>&1)"
fi

# Always recreate the virtual environment to ensure it's properly set up
log "Recreating virtual environment..."
if [ -d "$VENV_DIR" ]; then
  log "Removing existing virtual environment..."
  rm -rf "$VENV_DIR" || handle_error "Failed to remove existing virtual environment"
fi

log "Creating new virtual environment in $VENV_DIR..."
$PYTHON_PATH -m venv "$VENV_DIR" || handle_error "Failed to create virtual environment"
log "Virtual environment created successfully."

# Activate virtual environment
log "Activating virtual environment..."
source "$VENV_DIR/bin/activate" || handle_error "Failed to activate virtual environment"

# Verify Python path is from virtual environment
PYTHON_PATH_AFTER_ACTIVATION=$(which python)
log "Python path after activation: $PYTHON_PATH_AFTER_ACTIVATION"

if [[ "$PYTHON_PATH_AFTER_ACTIVATION" != *"$VENV_DIR"* ]]; then
  log "WARNING: Python path is not from virtual environment. Trying alternative activation method..."
  export PATH="$VENV_DIR/bin:$PATH"
  PYTHON_PATH_AFTER_ACTIVATION=$(which python)
  log "Python path after PATH update: $PYTHON_PATH_AFTER_ACTIVATION"
fi

# Install required packages in virtual environment
log "Installing required packages in virtual environment..."
python -m ensurepip --upgrade || handle_error "Failed to ensure pip is installed"
python -m pip install --upgrade pip || handle_error "Failed to upgrade pip"

# Check if requirements.txt exists
if [ -f "requirements.txt" ]; then
  log "Installing packages from requirements.txt..."
  python -m pip install -r requirements.txt || handle_error "Failed to install requirements"
else
  log "WARNING: requirements.txt not found. Installing basic packages..."
  python -m pip install streamlit pandas numpy || handle_error "Failed to install basic packages"
fi

# Set PYTHONPATH
export PYTHONPATH="$APP_DIR:$APP_DIR/src:$APP_DIR"
log "PYTHONPATH set to: $PYTHONPATH"

# Check if main.py exists
if [ ! -f "src/app/main.py" ]; then
  log "WARNING: src/app/main.py not found. Checking for alternative entry points..."
  
  # Look for Python files that might be entry points
  if [ -f "run.py" ]; then
    log "Found run.py, using it as entry point..."
    ENTRY_POINT="run.py"
  else
    log "ERROR: No suitable entry point found. Please check your application structure."
    exit 1
  fi
else
  ENTRY_POINT="src/app/main.py"
fi

# Start Streamlit application
log "Starting Streamlit application from $ENTRY_POINT..."
python -m streamlit run "$ENTRY_POINT" --server.port 8000 --server.enableCORS false --server.address 0.0.0.0 || handle_error "Failed to start Streamlit"

# If Streamlit fails, try running the Python script directly
if [ $? -ne 0 ]; then
  log "Streamlit failed, trying to run the Python script directly..."
  python "$ENTRY_POINT" || handle_error "Failed to run the Python script directly"
fi

log "Application startup process completed." 