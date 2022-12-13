#!/bin/bash

set -e

source $SNAP/connectedhomeip/python_env/bin/activate_snap

echo "venv: $VIRTUAL_ENV"

python3 -u $SNAP/bin/lighting.py
