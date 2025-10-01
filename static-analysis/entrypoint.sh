#!/bin/sh
set -e
set -x

pwd
ls /static_analysis
#Set Up
rm -f $DB_NAME
python3 create_duckdb.py $DB_NAME
python3 parse_yml_to_db.py semgrep-rules.yml $DB_NAME
semgrep ci

#Go Through all Plugins
for i in `seq 0 $(($NUM_PLUGINS - 1))`
do
    echo "Analyzing plugin number $i"
    python3 download-unzip-and-infocreation.py plugins_sorted.csv $i
    slug=$(python3 get_slug.py plugins_sorted.csv $i)
    #I am actually not sure about excluding the tests directory
    semgrep --config=semgrep-rules.yml --json  --include='*.php' --exclude='*/vendor/*' --exclude='*/tests/*' --output="./results/$slug/semgrep.json" ./plugins
    rm -rf plugins
done

#Aggregate semgrep json output
python3 parse_json_to_db.py results
#aggregate joern output

#Data Analysis over the findings in .db

#Keeps Docker container Running
exec tail -f /dev/null