#!/bin/bash

APPDIR=$(dirname $0)

export PATH=${HOME}/local/bin:${PATH}
export LD_LIBRARY_PATH=${HOME}/local/lib:${LD_LIBRARY_PATH}

cd ${APPDIR}

python launcher.py $@
