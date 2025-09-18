#!/bin/sh
set -e
set -x

pwd
ls
for i in `seq 0 $NUM_PLUGINS`
do
    echo "Analyzing plugin number $i"
    python3 download-and-unzip.py plugins_sorted.csv $i
    semgrep --config semgrep-rules.yml ./plugins > ./results/test-$i.txt
    rm -rf plugins
done

exec tail -f /dev/null