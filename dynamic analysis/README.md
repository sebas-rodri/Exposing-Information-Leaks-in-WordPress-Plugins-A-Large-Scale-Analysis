# Dynamic Analysis
Only start after static analysis, otherwise AJAX wont work properly, make sure to copy/move results.db into this directory. <br>
To run use `./runscript.sh` togheter with the `$NUM_PLUGINS` env variable to indicate how many plugins should be analyzed. Start the script inside of a tmux session <br>
3 main categories are tested: <br>
1. CRUD operations provided by WordPress CLI
2. AJAX endpoints
3. REST endpoints
<br>
Functions are hooked using [User Operations for Zend(uopz)](https://www.php.net/manual/de/book.uopz.php), this provides insights aboput which php functions are used during the execution of the plugins.

