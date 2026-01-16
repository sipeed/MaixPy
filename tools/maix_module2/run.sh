#!/bin/bash

maixpy_root="."
python -u -c "exec('import sys;sys.path.insert(0, \'$maixpy_root\');'+open('$1', 'r').read())"


