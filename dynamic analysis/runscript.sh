#Dowload Plugin
#Start Wordpress with seeded instance
#Activate security plugins > pipe results into findings
#Runner with f
#Search for created log files if there are any save information in duckdb.db to analyze later and for later analyzing
#Gracefully stop container
#Delete Plugin

NUM_PLUGINS=${NUM_PLUGINS:-1}
#set up part
docker compose stop
docker volume prune -a -f 
echo "Analyzing $NUM_PLUGINS plugins"
for i in `seq 0 $(($NUM_PLUGINS-1))`
do
    if [ -f "./shared_runner_watcher/dynamic_test_findings.jsonl" ]; then
        rm ./shared_runner_watcher/dynamic_test_findings.jsonl
    fi
    echo "Analyzing plugin number $i"
    python3 ../static-analysis/python_scripts/download-unzip-and-infocreation.py plugins_sorted.csv $i
    slug=$(python3 ../static-analysis/python_scripts/get_slug.py plugins_sorted.csv $i)
    echo "Analysing plugin: ${slug}"
    docker volume prune -a -f
    export PLUGIN_SLUG=${slug} 
    PLUGIN_SLUG=${slug} docker compose -p wp-${slug} -f docker-compose.yml up --build -d
    # Wait for Runner to stop
    while docker compose -p wp-${slug} -f docker-compose.yml ps --services --filter "status=running" | grep -q runner; do
        echo "Waiting for wp-${slug}-runner-1 container to complete..."
        sleep 2
    done
    echo "\n ________________________________\n${slug}\n" >> ./logs/cli-container.log
    docker logs wp-${slug}-wordpress-cli-1 >> ./logs/cli-container.log
    echo "\n ________________________________\n${slug}\n" >> ./logs/watcher-container.log
    docker logs wp-${slug}-watcher-1 >> ./logs/watcher-container.log
    echo "\n ________________________________\n${slug}\n" >> ./logs/runner-container.log
    docker logs wp-${slug}-runner-1 >> ./logs/runner-container.log

    rm -rf plugins
    rm -rf shared-wordpress
    rm -rf results
    docker compose -p wp-${slug} down
    docker network prune -f 
    sleep 1
done


