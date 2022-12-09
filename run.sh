#!/bin/bash

set -ev

source $SNAP/connectedhomeip/python_env/bin/activate_snap

echo "venv: $VIRTUAL_ENV"

python3 $SNAP/bin/lighting.py
