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

# Check for available Python versions
echo "Checking for available Python versions..."
if command -v python3 &> /dev/null; then
  PYTHON_PATH="python3"
  echo "Using Python 3:"
  $PYTHON_PATH --version
elif command -v python &> /dev/null; then
  PYTHON_PATH="python"
  echo "Using default Python:"
  $PYTHON_PATH --version
else
  echo "No Python found. Installing Python 3.9..."
  apt-get update
  apt-get install -y python3.9 python3.9-venv
  PYTHON_PATH="python3.9"
  echo "Using Python 3.9:"
  $PYTHON_PATH --version
fi

# Create virtual environment if it doesn't exist
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
  echo "Creating new virtual environment..."
  $PYTHON_PATH -m venv venv
else
  echo "Virtual environment already exists."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install required packages in virtual environment
echo "Installing required packages in virtual environment..."
pip install --upgrade pip
pip install -r requirements.txt || echo "Failed to install requirements, continuing..."

# Set PYTHONPATH
export PYTHONPATH=/home/site/wwwroot:/home/site/wwwroot/src:/home/site/wwwroot

# Start Streamlit application
echo "Starting Streamlit application..."
python -m streamlit run src/app/main.py --server.port 8000 --server.enableCORS false --server.address 0.0.0.0 || echo "Failed to start Streamlit, trying alternative method..."

# If Streamlit fails, try running the Python script directly
if [ $? -ne 0 ]; then
  echo "Trying to run the Python script directly..."
  python src/app/main.py || echo "Failed to run the Python script directly."
fi 