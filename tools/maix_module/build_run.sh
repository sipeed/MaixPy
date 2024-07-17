#!/bin/bash

maixpy_root="."
cd $maixpy_root python project.py build && python -u -c "exec('import sys;sys.path.insert(0, \'$maixpy_root\');'+open('$1', 'r').read())"


