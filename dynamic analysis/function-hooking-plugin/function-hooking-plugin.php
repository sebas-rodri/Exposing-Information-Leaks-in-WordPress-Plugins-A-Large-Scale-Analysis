<?php
/*
Plugin Name:       function-hooking-plugin
Description:       This plugin hooks into certain sinks with uopz php extension
Version:           1.0
Author:            Sebastian Rodriguez
Author URI:        https://sebastian-rodriguez.com/
 */

function function_hook_prefix_function_to_run()
{
    //just for setup
}

register_activation_hook(
    __FILE__,
    'function_hook_prefix_function_to_run'
);

register_deactivation_hook(
    __FILE__,
    'function_hook_prefix_function_to_run'
);

function setup_minimal_hooks()
{
    if (!extension_loaded('uopz')) {
        echo 'uopz not loaded';
        return;
    }
    //TODO: Add all relevant sinks with better information

    $log_file = WP_CONTENT_DIR . '/function-hooks.log';

    // Hook wp_upload_dir
    uopz_set_hook('wp_upload_dir', function ($time = null, $create_dir = true, $refresh_cache = false) use ($log_file) {
        $log_entry = [
            'timestamp' => date('Y-m-d H:i:s'),
            'function' => 'wp_upload_dir',
            'arguments' => ['time' => $time, 'create_dir' => $create_dir, 'refresh_cache' => $refresh_cache]
        ];
        file_put_contents($log_file, json_encode($log_entry) . "\n", FILE_APPEND | LOCK_EX);
    });

    // Hook file_put_contents
    uopz_set_hook('file_put_contents', function ($filename, $data, $flags = 0, $context = null) use ($log_file) {
        $log_entry = [
            'timestamp' => date('Y-m-d H:i:s'),
            'function' => 'file_put_contents',
            'arguments' => ['filename' => $filename, 'data_length' => strlen($data)]
        ];
        file_put_contents($log_file, json_encode($log_entry) . "\n", FILE_APPEND | LOCK_EX);
    });

    //Hook fwrite

    //Hook fopen maybe

    //Hook fprintf
}

// Initialize hooks when plugins are loaded
add_action('plugins_loaded', 'setup_minimal_hooks');

register_activation_hook(__FILE__, 'function_hook_prefix_function_to_run');
register_deactivation_hook(__FILE__, 'function_hook_prefix_function_to_run');