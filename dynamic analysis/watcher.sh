#!/bin/bash
#https://stackoverflow.com/questions/8699293/how-to-monitor-a-complete-directory-tree-for-changes-in-linux
inotifywait -m -r -e modify,create,delete,move /var/www/html/wp-content --format '%w%f %e %T' --timefmt '%Y-%m-%d %H:%M:%S' | while read file event time
do
    echo "[$time] File changed: $file (Event: $event)"
    echo "[$time] $event: $file" >> /tmp/file_changes.log
    cat "$file"
done
