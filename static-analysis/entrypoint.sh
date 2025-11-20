#!/bin/sh
set -e
set -x

pwd
ls /static_analysis
#Set Up
rm -f $DB_NAME
python3 create_duckdb.py $DB_NAME
python3 parse_yml_to_db.py semgrep-rules.yml $DB_NAME
semgrep login

#Go Through all Plugins
for i in `seq 0 $(($NUM_PLUGINS - 1))`
do
    echo "Analyzing plugin number $i"
    python3 download-unzip-and-infocreation.py plugins_sorted.csv $i
    slug=$(python3 get_slug.py plugins_sorted.csv $i)
    export slug;
    #I am actually not sure about excluding the tests directory
    semgrep --config=semgrep-rules.yml --json  --include='*.php' --exclude='*/vendor/*' --exclude='*/tests/*' --output="./results/$slug/semgrep.json" ./plugins
    semgrep --config=semgrep-ajax-first.yml --json  --include='*.php' --exclude='*/vendor/*' --exclude='*/tests/*' --output="./results/$slug/ajax.json" ./plugins
    python create_semgrep_rule_dynamic.py
    j=0
    for file in "./results/$slug/semgrep-rules-ajax/"*; do
        if [ -f "$file" ]; then     
        semgrep --config=$file --json  --include='*.php' --exclude='*/vendor/*' --exclude='*/tests/*' --output="./results/$slug/ajax-findings/$j.json" ./plugins || echo "Semgrep failed for rule $file"
        j=$(( j + 1))
        fi
    done 
    rm -rf plugins
done

#Aggregate semgrep json output
python3 parse_json_to_db.py results
#aggregate joern output


#Keeps Docker container Running
exec tail -f /dev/null