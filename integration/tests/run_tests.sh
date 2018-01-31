#!/bin/bash

set -e 
set -x

DIR=$(pwd)
echo ${DIR}
source activate asteroid

python "${DIR}/test_graphics.py"
# python test_polyhedron_functions.py
# python test_searching.py
# python test_wavefront.py
