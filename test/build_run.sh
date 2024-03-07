#!/bin/bash

cd .. && python project.py rebuild && python -u -c "exec('import sys;sys.path.insert(0, \'.\');'+open('test/$1', 'r').read())" && cd test


