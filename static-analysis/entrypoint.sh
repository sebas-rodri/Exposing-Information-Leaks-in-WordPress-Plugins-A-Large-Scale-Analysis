#!/bin/sh
set -e
set -x

pwd
ls /static_analysis
#Create DB File
rm -f $DB_NAME
python3 create_duckdb.py $DB_NAME
python3 parse_yml_to_db.py semgrep-rules.yml $DB_NAME
for i in `seq 0 $(($NUM_PLUGINS - 1))`
do
    echo "Analyzing plugin number $i"
    python3 download-unzip-and-infocreation.py plugins_sorted.csv $i
    slug=$(python3 get_slug.py plugins_sorted.csv $i)
    #I am actually not sure about excluding the tests directory
    semgrep --config=semgrep-rules.yml --json  --include='*.php' --exclude='*/vendor/*' --exclude='*/tests/*' --output="./results/$slug/semgrep.json" ./plugins
    rm -rf plugins
done

python3 parse_json_to_db.py results
#Aggregate semgrep json output
#aggregate joern output

#Keeps Docker container Running
exec tail -f /dev/null