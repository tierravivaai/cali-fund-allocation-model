#!/bin/bash

# Cali Fund Allocation Model - Streamlit Dashboard Startup Script
# Usage: ./start_dashboard.sh

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check Python and virtual environment
echo "Starting Cali Fund Allocation Dashboard..."

if [ ! -d ".venv" ]; then
    echo "Error: .venv directory not found. Please set up the virtual environment first."
    echo "Run: python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check if Streamlit is installed
if ! .venv/bin/python -c "import streamlit" 2>/dev/null; then
    echo "Streamlit not installed. Installing..."
    .venv/bin/pip install streamlit
fi

# Start the dashboard
echo "Launching Streamlit dashboard..."
echo "Dashboard will be available at: http://localhost:8501"
echo "Press Ctrl+C to stop the server"
echo ""

.venv/bin/streamlit run dashboard.py
