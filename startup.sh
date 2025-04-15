#!/bin/bash

# Set environment variables
WEBAPP_NAME="slifit"
RESOURCE_GROUP="slihackathon-2025-team2-rg"

# Print current directory
pwd
echo "Current directory: $(pwd)"

# List directory contents
ls -la
echo "Directory contents: total $(ls -la | wc -l)"

# Search for extracted deployment directory
echo "Searching for extracted deployment directory..."
head -n 1
find /tmp -maxdepth 1 -type d -name '8dd7b4*' -o -name zipdeploy
sort -r
LATEST_TMP_DIR=$(find /tmp -maxdepth 1 -type d -name '8dd7b4*' -o -name zipdeploy | sort -r | head -n 1)

if [ -n "$LATEST_TMP_DIR" ]; then
  echo "Found deployment directory: $LATEST_TMP_DIR"
  echo "Contents of $LATEST_TMP_DIR:"
  ls -la "$LATEST_TMP_DIR"
  
  echo "Copying files from $LATEST_TMP_DIR to /home/site/wwwroot..."
  
  # Check if extracted directory exists
  if [ -d "$LATEST_TMP_DIR/extracted" ]; then
    # Copy all files from extracted directory to wwwroot
    cp -rv "$LATEST_TMP_DIR/extracted/"* /home/site/wwwroot/
    echo "Copy complete. Directory contents after copy:"
    ls -la /home/site/wwwroot
  else
    echo "No extracted directory found in $LATEST_TMP_DIR"
  fi
else
  echo "No deployment directory found"
fi

# Change to wwwroot directory
cd /home/site/wwwroot

# Check if startup.sh exists and set execute permissions
if [ -f "startup.sh" ]; then
  echo "Found startup.sh, setting execute permissions..."
  chmod +x startup.sh
fi

# Use system Python 3.9 instead of creating a virtual environment
echo "Using system Python 3.9..."
PYTHON_PATH="/usr/bin/python3.9"

# Check Python version
echo "Python version:"
$PYTHON_PATH --version

# Install required packages using system Python
echo "Installing required packages..."
$PYTHON_PATH -m pip install --upgrade pip
$PYTHON_PATH -m pip install -r requirements.txt

# Set PYTHONPATH
export PYTHONPATH=/home/site/wwwroot:/home/site/wwwroot/src:/home/site/wwwroot

# Check installed packages
echo "Installed packages:"
$PYTHON_PATH -m pip list

# Check Streamlit version
echo "Streamlit version:"
$PYTHON_PATH -m streamlit --version

# Start Streamlit application
echo "Starting Streamlit application..."
$PYTHON_PATH -m streamlit run src/app/main.py --server.port 8000 --server.enableCORS false --server.address 0.0.0.0 