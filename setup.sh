#!/usr/bin/env bash
if (( $# == 2 ))
then
    mkdir -p build && cd build && cmake -G $1 -DMAYA_VERSION=$2 ../ 
else
    echo "Error: you must provide either an IDE and Maya version"
    exit 1
fi