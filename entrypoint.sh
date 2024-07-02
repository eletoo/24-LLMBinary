#!/bin/bash

set -ex

for file in /dataset/*.json; do
   python main.py NoFun --dataset $file --results /out/$(basename $file .json).result --output /out/$(basename $file .json).output
done

for file in /out/*.output; do
   mkdir -p /out/plots/$(basename $file .output)
   python ELAB.py $file /out/plots/$(basename $file .output)/
done