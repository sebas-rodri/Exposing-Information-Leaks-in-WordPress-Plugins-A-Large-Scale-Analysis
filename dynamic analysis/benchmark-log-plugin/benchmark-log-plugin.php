<?php
/*
 * Plugin Name: benchmark-log-plugin
 */

function pluginprefix_function_to_run() {
    //just for setup
}

function log_bench_event(string $event, array $data = [] ) {
    $upload_dir = wp_upload_dir();
     
     // Create log entry
     $log_entry = [
         'timestamp' => date('Y-m-d H:i:s'),
         'event' => $event,
         'upload_dir' => $upload_dir,
         'request_uri' => $_SERVER['REQUEST_URI'] ?? '',
         'user_agent' => $_SERVER['HTTP_USER_AGENT'] ?? '',
         'data' => $data,
     ];
     
     // Write to log file
     $log_file = WP_CONTENT_DIR . '/benchmark-log.log';
     file_put_contents($log_file, json_encode($log_entry) . "\n", FILE_APPEND | LOCK_EX);
}
//It seems one have to add argument count when there are multiple parameters,
//prio is 10 

/********************************************+
 * Users
 ********************************************/
//Registration
function benchmark_user_register_callback($user_id) {
    log_bench_event('user_register', [
        'user_id' => $user_id,
    ]);
}


function benchmark_profile_update_callback($user_id, $old_user_data, $user_data) {
    //WPUser Object $old_user_data
    log_bench_event('profile_update', [
        'user_id' => $user_id,
        'old_user_login' => $old_user_data->user_login,
        'old_user_email' => $old_user_data->user_email,
        'old_display_name' => $old_user_data->display_name,
        'userdata' => $user_data
    ]);
}

function benchmark_personal_options_update_callback($user_id) {
    log_bench_event('personal_options_update', [
        'user_id' => $user_id,
        'updated_fields' => $_POST,
    ]);
}

function benchmark_edit_user_profile_update_callback($user_id) {
    log_bench_event('edit_user_profile_update', [
        'user_id' => $user_id,
        'updated_fields' => $_POST,
    ]);
}

function benchmark_user_profile_update_errors_callback($errors, $update, $user) {
    //WP Error Object $errors
    log_bench_event('user_profile_update_errors', [
        'user_id' => $user->ID, 
        'is_update' => $update,
        'error_codes' => $errors->get_error_codes(),  
        'error_messages' => $errors->get_error_messages(),
        'attempted_fields' => $_POST,
    ]);
}

function benchmark_wp_login_callback($user_login, $user) {
    log_bench_event('wp_login', [
        'user_login' => $user_login,
        'user_id' => $user->ID,
        'user_email' => $user->user_email,
        'user_roles' => $user->roles,
    ]);
}

function benchmark_wp_login_failed_callback($username, $error) {
    log_bench_event('wp_login_failed', [
        'username' => $username,
        'error_code' => $error->get_error_code(),
        'error_message' => $error->get_error_message(),
    ]);
}

function benchmark_wp_logout_callback($user_id) {
    log_bench_event('wp_logout', [
        'user_id' => $user_id,
    ]);
}

function benchmark_lostpassword_post_callback($errors, $user_data) {
    log_bench_event('lostpassword_post', [
        'user_login' => $user_data->user_login ?? '',
        'user_email' => $user_data->user_email ?? '',
        'user_id' => $user_data->ID ?? null,
        'has_errors' => !empty($errors->get_error_codes()),
        'error_codes' => $errors->get_error_codes(),
    ]);
}

function benchmark_password_reset_callback($user, $new_pass) {
    log_bench_event('password_reset', [
        'user_id' => $user->ID,
        'user_login' => $user->user_login,
        'user_email' => $user->user_email,
        'new_password'=> $new_pass,
    ]);
}

add_action('user_register', 'benchmark_user_register_callback');
add_action('profile_update', 'benchmark_profile_update_callback', 10, 3);
add_action('personal_options_update', 'benchmark_personal_options_update_callback');
add_action('edit_user_profile_update', 'benchmark_edit_user_profile_update_callback');
add_action('user_profile_update_errors', 'benchmark_user_profile_update_errors_callback', 10, 3);
add_action('wp_login', 'benchmark_wp_login_callback', 10, 2);
add_action('wp_login_failed', 'benchmark_wp_login_failed_callback', 10, 2);
add_action('wp_logout', 'benchmark_wp_logout_callback');
add_action('lostpassword_post', 'benchmark_lostpassword_post_callback', 10, 2);
add_action('password_reset', 'benchmark_password_reset_callback', 10, 2);

/********************************************+
 * CRUD
 ********************************************/
// Posts
add_action('save_post', function ($post_id, $post, $update) {
    log_bench_event('save_post', [
        'post_id' => $post_id,
        'post_title' => $post->post_title,
        'post_status' => $post->post_status,
        'post_type' => $post->post_type,
        'post_author' => $post->post_author,
        'is_update' => $update,
    ]);
}, 10, 3);

add_action('delete_post', function ($post_id, $post) {
    log_bench_event('delete_post', [
        'post_id' => $post_id,
        'post_title' => $post->post_title,
        'post_status' => $post->post_status,
        'post_type' => $post->post_type,
        'post_author' => $post->post_author,
    ]);
}, 10, 2);

add_action('untrashed_post', function ($post_id, $previous_status) {
    $post = get_post($post_id);
    log_bench_event('untrashed_post', [
        'post_id' => $post_id,
        'post_title' => $post->post_title ?? '',
        'post_type' => $post->post_type ?? '',
        'previous_status' => $previous_status,
    ]);
}, 10, 2);

// Comments
add_action('comment_post', function ($comment_id, $comment_approved, $commentdata) {
    log_bench_event('comment_post', [
        'comment_id' => $comment_id,
        'comment_approved' => $comment_approved,
        'comment_data' => $commentdata,
    ]);
}, 10, 3);

add_action('delete_comment', function ($comment_id, $comment) {
    log_bench_event('delete_comment', [
        'comment_id' => $comment_id,
        'comment_post_ID' => $comment->comment_post_ID,
        'comment_author' => $comment->comment_author,
        'comment_author_email' => $comment->comment_author_email,
        'comment_author_IP' => $comment->comment_author_IP,
        'comment_date' => $comment->comment_date,
    ]);
}, 10, 2);

add_action('edit_comment', function ($comment_id, $data) {
    log_bench_event('edit_comment', [
        'comment_id' => $comment_id,
        'updated_data' => $data,
    ]);
}, 10, 2);
/********************************************
 * AJAX
 ********************************************/
// Logged-in users
add_action('wp_ajax_test', function() {
    echo 'Hello from wp_ajax_test';
    wp_die();
});
// Guests (not logged in)
add_action('wp_ajax_nopriv_test', function() {
    echo 'Hello from wp_ajax_nopriv_test';
    wp_die();
});
/********************************************+
 * REST
 ********************************************/

//GET
add_action('rest_api_init', function() {
    register_rest_route('benchmark/v1', '/test', [
        'methods'  => 'GET',
        'callback' => function( WP_REST_Request $request ) {
            log_bench_event('benchmark/v1/test',[]);
            return rest_ensure_response([
                'success' => true,
                'message' => 'Hello from benchmark/v1/test',
            ]);
        },
        'permission_callback' => '__return_true',
    ]);
});

//POST

register_activation_hook(
	__FILE__,
	'pluginprefix_function_to_run'
);

register_deactivation_hook(
	__FILE__,
	'pluginprefix_function_to_run'
);




/*
My approach will be using just wordpress api, and adding callbacks to known hooks add_action('hook', 'callback_function')
But what to do about
 */

