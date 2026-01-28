# Static Analysis
This directory contains the necessary code conduct the static analysis, and stores the information in a duckdb database that is later used to get the results of the experiments. [Semgrep](https://semgrep.dev/docs/) as the tool the static analysis.
Additionaly all the information about the AJAX routes and the needed arguments is gathered, and stored in the tables `ajax_routes` and `ajax_routes_arguments`.

## How to run 
1. Setup:
    - Run `python3 scripts/sort-plugins-by-download.py` from the root directory. This will create a csv list of the top 10,000 WordPress plugins sorted by download.
    - Inside the Dockerfile set `START_PLUGIN` and `NUM_PLUGINS` to desired Intervall that should be analyzed
    - Create a Semgrep Token and store it in a file called `secrets.env` where the content looks like `SEMGREP_APP_TOKEN="YourTOKEN"`
2. Start Docker Container with `docker compose up --build -d`

---
## Description of the Implementation
The Dockerfile contains all the needed dependencies and starts at `entrypoint.sh`. 
First the DB is created and the semgrep rules are parsed and stored in the table `rules`, additionaly semgrep logs in with the provided Token.
It is looped over the provided Intervall. Inside each iteration one WordPress plugin is downloaded and unziped using `python_scripts/download-unzip-and-infocreation.py`, additionaly information about the plugin is created in a json format.
Then semgrep is executed using the provided rules, the rules are described below.
For the AJAX routes the implementation needs two steps:
1. It is searched for AJAX Routes, using `add_action($HOOK, '$NAME')`, where `$HOOK` needs to start with `wp_ajax`.
2. For each found `$HOOK` one semgrep rule is created dynamicly that searches for needed arguments inside the function provided (`$NAME`). It is searched for argument names inside of FILES, REQUEST, POST, GET

Finally after iterating over all plugins, that json output created by the scripts and by semgrep is parsed into the database for later use and the container just keeps running.

## Description of the Semgrep Rules
Primarly it is searched for file write sinks that contain the word `log`, there is a total of 10 semgrep rules:
- `file-put-contents_`: Will gather all lines containing file_put_contents() if the provided filename contains `log`
- `file-put-contents_log-file-var-assignment`: Extention of the rule above, with the difference that the passed filename has to be a variable, and has to be created by other variables or hardcoded paths that contain `log`
- `fopen_var-assignment`: Will match if the passed filename is a variable, and the creation contains `log`.
- `fwrite_with-fopen`: Matches cases where a file handle is assigned to a variable using `fopen()` with a filename containing the substring `log`, and this variable is subsequently used in a call to `fwrite()`.
- `fprintf_with-fopen`:  Matches cases where a file handle is assigned to a variable using `fopen()` with a filename containing the substring `log`, and this variable is subsequently used in a call to `fprintf()`.
- `fputs_with-fopen`: Matches cases where a file handle is assigned to a variable using `fopen()` with a filename containing the substring `log`, and this variable is subsequently used in a call to `fputs()`.
- `wp-upload-dir_`: Matches if `wp_upload_dir(...)`is used.
- `hardcoded-wp-content-path`: Matches any lines containing the substring `wp-content`
- `WP-DEBUG_enabling`: Matches if the `WP_DEBUG` is set as true
- ` WP-DEBUG-LOG_enabling`: Matches if the `WP_DEBUG_LOG` is set as true

Note: [Debugging](https://developer.wordpress.org/advanced-administration/debug/debug-wordpress/) in WordPress can be done using the constant WP_DEBUG and WP_DEBUG_LOG, but these contants should be defined in `wp-config.php`.
---
## Future Work:
- The Dockerfile provides a ready to use [Joern](https://docs.joern.io/) installation, this could be a really useful tool which wasn't used here
- There is a none zero chance, that not all logfiles have to contain the substring `log`, but this was out of scope for the thesis experiments.
- It would be useful to extend the approach to get in all cases, (if possible) the actual filepath used in the filewrite sinks, rather then just variables containing the path.