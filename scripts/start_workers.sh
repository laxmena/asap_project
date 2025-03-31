#!/bin/bash

# Set environment variable to prevent forking issues on macOS
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

# Kill any existing RQ workers
pkill -f "python.*main_worker.py"

# Small delay to ensure previous workers are killed
sleep 1

echo "Starting main worker..."
# Run the worker in foreground to see logs
python src/workers/main_worker.py 