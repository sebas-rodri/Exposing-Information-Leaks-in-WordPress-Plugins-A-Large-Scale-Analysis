#!/bin/sh
set -euo pipefail
set -x

sleep 7;
wp core multisite-install --path="/var/www/html" --url="http://localhost:8080" --title="Dynamic Analysis ${PLUGIN_SLUG}" --admin_user=admin --admin_password=secret --admin_email=foo@bar.com --allow-root;
#Debug
ls -la /var/www/html/wp-content/plugins/
wp plugin list --allow-root
###################################
wp plugin activate benchmark-log-plugin --allow-root
wp plugin activate ${PLUGIN_SLUG} --allow-root

#seed database with wp-api
#TODO: 
#wp db check
#wp db reset --yes


wp site create --slug=holamundo
wp site list --field=url

#User creation one per role
wp user create admin2 admin@admin.de --role=administrator --user_pass=administrator --nickname=Al --first_name=Alice --last_name=Austen
wp user create editor editor@editor.de --role=editor --user_pass=editor --nickname=Ed --first_name=Eddie --last_name=Editor
wp user create author author@author.de --role=author --user_pass=author --nickname=Au --first_name=Arthur --last_name=Author
wp user create contributor contributor@contributor.de --role=contributor --user_pass=contributor --nickname=Co --first_name=Connor --last_name=Contributor  
wp user create subscriber subscriber@subscriber.de --role=subscriber --user_pass=subscriber --nickname=Su --first_name=Susan --last_name=Subscriber

wp user generate --count=10
wp post generate --count=10 --post_type=page

wp plugin activate function-hooking-plugin --allow-root
