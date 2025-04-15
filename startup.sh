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
VENV_DIR="$APP_DIR/.venv"
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
  apt-get install -y python3.9 || handle_error "Failed to install Python 3.9"
  PYTHON_PATH="python3.9"
  log "Using Python 3.9: $($PYTHON_PATH --version 2>&1)"
fi

# Create a simple virtual environment using a different approach
log "Setting up Python environment..."
mkdir -p "$VENV_DIR/lib" || handle_error "Failed to create virtual environment directory"

# Create a simple activate script
cat > "$VENV_DIR/bin/activate" << 'EOF'
# This file must be used with "source bin/activate" *from bash*
# you cannot run it directly

deactivate () {
    # reset old environment variables
    if [ -n "${_OLD_VIRTUAL_PATH:-}" ] ; then
        PATH="${_OLD_VIRTUAL_PATH:-}"
        export PATH
        unset _OLD_VIRTUAL_PATH
    fi
    if [ -n "${_OLD_VIRTUAL_PYTHONHOME:-}" ] ; then
        PYTHONHOME="${_OLD_VIRTUAL_PYTHONHOME:-}"
        export PYTHONHOME
        unset _OLD_VIRTUAL_PYTHONHOME
    fi

    # This should detect bash and zsh, which have a hash command that must
    # be called to get it to forget past commands.  Without forgetting
    # past commands the $PATH changes we made may not be respected
    if [ -n "${BASH:-}" -o -n "${ZSH_VERSION:-}" ] ; then
        hash -r 2> /dev/null
    fi

    if [ -n "${_OLD_VIRTUAL_PS1:-}" ] ; then
        PS1="${_OLD_VIRTUAL_PS1:-}"
        export PS1
        unset _OLD_VIRTUAL_PS1
    fi

    unset VIRTUAL_ENV
    if [ ! "${1:-}" = "nondestructive" ] ; then
    # Self destruct!
        unset -f deactivate
    fi
}

# unset irrelevant variables
deactivate nondestructive

VIRTUAL_ENV="$VENV_DIR"
export VIRTUAL_ENV

_OLD_VIRTUAL_PATH="$PATH"
PATH="$VIRTUAL_ENV/bin:$PATH"
export PATH

# unset PYTHONHOME if set
# this will fail if PYTHONHOME is set to the empty string (which is bad anyway)
# could use `if (set -u; : $PYTHONHOME) ;` in bash
if [ -n "${PYTHONHOME:-}" ] ; then
    _OLD_VIRTUAL_PYTHONHOME="${PYTHONHOME:-}"
    unset PYTHONHOME
fi

if [ -z "${VIRTUAL_ENV_DISABLE_PROMPT:-}" ] ; then
    _OLD_VIRTUAL_PS1="${PS1:-}"
    PS1="(.venv) ${PS1:-}"
    export PS1
fi

# This should detect bash and zsh, which have a hash command that must
# be called to get it to forget past commands.  Without forgetting
# past commands the $PATH changes we made may not be respected
if [ -n "${BASH:-}" -o -n "${ZSH_VERSION:-}" ] ; then
    hash -r 2> /dev/null
fi
EOF

# Make the activate script executable
chmod +x "$VENV_DIR/bin/activate" || handle_error "Failed to make activate script executable"

# Create a simple pip script
mkdir -p "$VENV_DIR/bin" || handle_error "Failed to create bin directory"
cat > "$VENV_DIR/bin/pip" << 'EOF'
#!/bin/bash
python -m pip "$@"
EOF

# Make the pip script executable
chmod +x "$VENV_DIR/bin/pip" || handle_error "Failed to make pip script executable"

# Create a simple python script
cat > "$VENV_DIR/bin/python" << 'EOF'
#!/bin/bash
exec "$PYTHON_PATH" "$@"
EOF

# Make the python script executable
chmod +x "$VENV_DIR/bin/python" || handle_error "Failed to make python script executable"

# Activate the virtual environment
log "Activating virtual environment..."
source "$VENV_DIR/bin/activate" || handle_error "Failed to activate virtual environment"
log "Virtual environment activated. Python path: $(which python)"

# Install required packages
log "Installing required packages..."
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