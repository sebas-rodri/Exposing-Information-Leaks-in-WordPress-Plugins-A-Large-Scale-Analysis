# Comparison of State of the Art of security Plugins
This Directory can be used to test, if security plugins have functionality to find out about potential log leaks triggered trough third-party plugins.

For this purpose, I developed a minimal plugin that acts as Proof-of-Concept and creates logs when triggering WP commands, requesting REST or AJAX endpoints

As automating testing insn't allowed in most security plugins, and the tests run serverside, this plugin was used as a workaround. So this part relies heavily on manual testing.

## How to Use
1. Run docker compose up --build -d inside of this directory to start a fresh wordpress instance, delete possible existing volumes with docker volume prune beforehand. 
2. Install the wordpress, and install the security plugin that shall be used (e.g wordfence). (localhost:8080). Beforehand one should get the license keys needed for activation.
3. Trigger the plugin functionality that creates logs.

## Plugin Functionality that triggers log.
This plugin intentionally creates log files to benchmark filesystem write behavior in WordPress plugins. Log entries are written to WP_CONTENT_DIR/benchmark-log.log using both file_put_contents() and fopen()/fwrite().

- User-related actions:
  - User registration
  - User login and logout
  - Failed login attempts
  - Password reset and lost password flows
  - Profile updates and personal option changes
- Content-related actions:
  - Create, update, delete, and restore posts
  - Create, edit, and delete comments

### REST API Endpoints

- Namespace: `benchmark/v1`
- Exposed endpoints:
  - `GET /benchmark/v1/test`
  - `POST /benchmark/v1/echo`
- Log entries are created when:
  - A REST endpoint is req
  - Request parameters are processed

### AJAX Endpoints

- Registered AJAX actions:
  - `wp_ajax_test` (authenticated users)
  - `wp_ajax_nopriv_test` (unauthenticated users)
- Log entries are created when:
  - An AJAX request is sent to either endpoint

## Steps to reproduce:
1. Activate benchmark plugin
2. Activate Wordfence.
3. Wordfence


## Future Work:
- Extend the plugin functionality to cover all filewrite sinks
- Write an python requests script to trigger all the functionality