#!/bin/sh
set -euo pipefail
set -x

wait_if_change() {
    while [ -f ".change" ]; do
        sleep 1
    done

    if [ -f "/shared/current_test/current_test.txt" ]; then
        rm /shared/current_test/current_test.txt
    fi
}

sleep 5; #This is necessary to wait for other containers
wp core multisite-install --path="/var/www/html" --url="http://localhost:8080" --title="Dynamic Analysis ${PLUGIN_SLUG}" --admin_user=admin --admin_password=secret --admin_email=foo@bar.com --allow-root;
#Debug
ls -la /var/www/html/wp-content/plugins/
wp plugin list --allow-root
###################################
#wp plugin activate benchmark-log-plugin --allow-root
wp plugin activate ${PLUGIN_SLUG} --allow-root
#wp plugin activate function-hooking-plugin --allow-root

#pretty links

#seed database with wp-api
#TODO: 
#wp db check
#wp db reset --yes
pwd

echo '{"interface":"WP_CLI","method":"run","url":"wp site create --slug=holamundo","data":{}}' > /shared/current_test/current_test.txt
echo '{"interface":"WP_CLI","method":"run","url":"wp site create --slug=holamundo","data":{}}' > /shared/current_test/current_test.txt
wp site create --slug=holamundo
wait_if_change
#User creation one per role
echo '{"interface":"WP_CLI","method":"run","url":"wp user create admin2 admin@admin.de --role=administrator --user_pass=administrator --nickname=Al --first_name=Alice --last_name=Austen","data":{}}' > /shared/current_test/current_test.txt
wp user create admin2 admin@admin.de --role=administrator --user_pass=administrator --nickname=Al --first_name=Alice --last_name=Austen

wait_if_change
echo '{"interface":"WP_CLI","method":"run","url":"wp user create editor editor@editor.de --role=editor --user_pass=editor --nickname=Ed --first_name=Eddie --last_name=Editor","data":{}}' > /shared/current_test/current_test.txt
wp user create editor editor@editor.de --role=editor --user_pass=editor --nickname=Ed --first_name=Eddie --last_name=Editor

wait_if_change
echo '{"interface":"WP_CLI","method":"run","url":"wp user create author author@author.de --role=author --user_pass=author --nickname=Au --first_name=Arthur --last_name=Author","data":{}}' > /shared/current_test/current_test.txt
wp user create author author@author.de --role=author --user_pass=author --nickname=Au --first_name=Arthur --last_name=Author

wait_if_change
echo '{"interface":"WP_CLI","method":"run","url":"wp user create contributor contributor@contributor.de --role=contributor --user_pass=contributor --nickname=Co --first_name=Connor --last_name=Contributor","data":{}}' > /shared/current_test/current_test.txt
wp user create contributor contributor@contributor.de --role=contributor --user_pass=contributor --nickname=Co --first_name=Connor --last_name=Contributor  

wait_if_change
echo '{"interface":"WP_CLI","method":"run","url":"wp user create subscriber subscriber@subscriber.de --role=subscriber --user_pass=subscriber --nickname=Su --first_name=Susan --last_name=Subscriber","data":{}}' > /shared/current_test/current_test.txt
wp user create subscriber subscriber@subscriber.de --role=subscriber --user_pass=subscriber --nickname=Su --first_name=Susan --last_name=Subscriber

wait_if_change
echo '{"interface":"WP_CLI","method":"run","url":"wp user generate --count=1","data":{}}' > /shared/current_test/current_test.txt
wp user generate --count=1

wait_if_change
echo '{"interface":"WP_CLI","method":"run","url":"wp post generate --count=1 --post_type=page","data":{}}' > /shared/current_test/current_test.txt
wp post generate --count=1 --post_type=page

wait_if_change