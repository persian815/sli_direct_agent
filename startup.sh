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

# Create wwwroot directory if it doesn't exist
mkdir -p /home/site/wwwroot

# Copy files from current directory to wwwroot
echo "Copying files to /home/site/wwwroot..."
cp -rv * /home/site/wwwroot/ 2>/dev/null || echo "Some files could not be copied, continuing..."

# Change to wwwroot directory
cd /home/site/wwwroot

# Check if startup.sh exists and set execute permissions
if [ -f "startup.sh" ]; then
  echo "Found startup.sh, setting execute permissions..."
  chmod +x startup.sh
fi

# Use system Python 3.9
echo "Using system Python 3.9..."
PYTHON_PATH="/usr/bin/python3.9"

# Check Python version
echo "Python version:"
$PYTHON_PATH --version || echo "Python 3.9 not found, trying default Python..."

# If Python 3.9 is not available, use default Python
if ! command -v $PYTHON_PATH &> /dev/null; then
  PYTHON_PATH="python"
  echo "Using default Python:"
  $PYTHON_PATH --version
fi

# Install required packages
echo "Installing required packages..."
$PYTHON_PATH -m pip install --upgrade pip || echo "Failed to upgrade pip, continuing..."
$PYTHON_PATH -m pip install -r requirements.txt || echo "Failed to install requirements, continuing..."

# Set PYTHONPATH
export PYTHONPATH=/home/site/wwwroot:/home/site/wwwroot/src:/home/site/wwwroot

# Start Streamlit application
echo "Starting Streamlit application..."
$PYTHON_PATH -m streamlit run src/app/main.py --server.port 8000 --server.enableCORS false --server.address 0.0.0.0 || echo "Failed to start Streamlit, trying alternative method..."

# If Streamlit fails, try running the Python script directly
if [ $? -ne 0 ]; then
  echo "Trying to run the Python script directly..."
  $PYTHON_PATH src/app/main.py || echo "Failed to run the Python script directly."
fi 