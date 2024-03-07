#!/bin/bash

SCRIPT_PATH=$(realpath $(dirname "$0"))
python -u -c "exec('import sys;sys.path.insert(0, \'$SCRIPT_PATH/..\');'+open('$1', 'r').read())"


