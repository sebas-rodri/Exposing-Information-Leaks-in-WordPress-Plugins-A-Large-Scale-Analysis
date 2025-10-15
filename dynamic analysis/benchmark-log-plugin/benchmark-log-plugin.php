<?php
/*
 * Plugin Name: benchmark-log-plugin
 */

function pluginprefix_function_to_run() {
    //just for setup
}


function log_upload_dir_on_user_creation($user_id) {
     $upload_dir = wp_upload_dir(); //wp sink
     
     //filler
     $log_entry = [
         'timestamp' => date('Y-m-d H:i:s'),
         'event' => 'user_created',
         'user_id' => $user_id,
         'upload_dir' => $upload_dir,
         'request_uri' => $_SERVER['REQUEST_URI'] ?? '',
         'user_agent' => $_SERVER['HTTP_USER_AGENT'] ?? ''
     ];
     
     $log_file = WP_CONTENT_DIR . '/benchmark-log.log';
     file_put_contents($log_file, json_encode($log_entry) . "\n", FILE_APPEND | LOCK_EX);
 }

register_activation_hook(
	__FILE__,
	'pluginprefix_function_to_run'
);

register_deactivation_hook(
	__FILE__,
	'pluginprefix_function_to_run'
);



// Hook into user creation
add_action('user_register', 'log_upload_dir_on_user_creation');


