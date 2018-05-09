#!/usr/bin/env bash
mkdir -p build && cd build && cmake -G $1 -DMAYA_VERSION=$2 ../ 
