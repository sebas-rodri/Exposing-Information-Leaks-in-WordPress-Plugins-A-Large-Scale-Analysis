#!/bin/bash
zip_counter=0 #used for referencing later
chmod -R 777 /shared #This is needed bcs it makes problems with bind mount
#https://stackoverflow.com/questions/8699293/how-to-monitor-a-complete-directory-tree-for-changes-in-linux
inotifywait -m -r -e close_write,delete,move /var/www/html/wp-content /shared/current_test/ --format '%w%f %e %T' --timefmt '%Y-%m-%d %H:%M:%S' | while read file event time
do
    if [ -f "/shared/current_test/current_test.txt" ];then

        if [ "$file" = "/shared/current_test/current_test.txt" ];then
            echo "_____________________________________________________";echo "Current Test"; cat "$file" 
        else #Some file in wp-content changed
            #json
            touch .change
            zip_counter=$((zip_counter + 1))

            jq -c --arg file "$file" --arg event "$event" --arg zip_counter "$zip_counter" \
                '. + {name_of_changed_file: $file, type_of_operation: $event, zip_counter: $zip_counter}' \
                /shared/current_test/current_test.txt >> /shared/dynamic_test_findings.jsonl
            #zip contents
            interface=$(jq -r .interface /shared/current_test/current_test.txt)
            mkdir -p /shared/zip_files/${PLUGIN_SLUG}
            echo "zip_counter = $zip_counter"
            zip -0 /shared/zip_files/${PLUGIN_SLUG}/${interface}_${zip_counter}.zip $file #Maybe add flag -0 for no compression add feedback touch .change for runner if there is one sleep and check again
            rm .change
        fi
    fi

    #echo "[$time] File changed: $file (Event: $event)"
    #echo "[$time] $event: $file" >> /tmp/file_changes.log
done
