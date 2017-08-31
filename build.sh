#!/bin/bash - 
set -x
set -e

dir=abbrev-matcher
make -C $dir clean all
cp $dir/*.so python3

