#!/bin/sh
set -e
set -x

pwd
ls
for i in `seq 0 $NUM_PLUGINS`
do
    echo "Analyzing plugin number $i"
    python3 download-and-unzip.py plugins_sorted.csv $i
    #I am actually not sure about excluding the tests directory
    semgrep --config=semgrep-rules.yml --json --output --include='*.php' --exclude='*/vendor/*' --exclude='*/tests/*' ./results/test-$i.json ./plugins
    rm -rf plugins
done

#Aggregate semgrep json output
#aggregate joern output

exec tail -f /dev/null