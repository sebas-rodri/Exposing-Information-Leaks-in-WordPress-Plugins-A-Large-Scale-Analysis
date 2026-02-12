import duckdb
import matplotlib.pyplot as plt
import pandas as pd
import sys

def save_latex(latex_pf, filename):
    latex_pf = latex_pf.replace("\\begin{table}", "\\begin{table}[H]\n\\centering")
    latex_pf = latex_pf.replace("_", "\\_")
    with open(f"tables/{filename}.tex", "w") as f:
        f.write(latex_pf)

if len(sys.argv) != 2:
    print("Usage: python create_graphics.py <path_to_duckdb>")
    sys.exit(1)
    
con = duckdb.connect(sys.argv[1])

#Static Analysis
#Count Plugins that were handled successfully
ajax_route_count = con.sql("""
                            SELECT COUNT(*) AS Different_ajax_routes, COUNT(DISTINCT plugin_slug) AS NUM_PLUGINS_WITH_AJAX_ROUTES
                            FROM ajax_routes;
                            """).to_df()

ajax_arg_count = con.sql("""
                            SELECT COUNT(*) AS Different_ajax_route_arguments
                            FROM ajax_route_arguments;
                            """).to_df()

           
                            
plugin_count = con.sql("""
                       SELECT COUNT(*) AS NUM_PLUGINS FROM plugins;
                       """).to_df()

print(plugin_count)
#plugin_count.plot()
#plt.show()
#Range num downloaded from max to min also avg
max_min_avg_num_downloads = con.sql("""
                      SELECT MAX(num_downloads) as MAX_DOWNLOADS, MIN(num_downloads) as MIN_DOWNLOADS, ceil(AVG(num_downloads)) as AVG
                      FROM plugins;
                      """).to_df()
print(max_min_avg_num_downloads)

latex_max_min_avg_num_downloads = max_min_avg_num_downloads.to_latex(index=False, caption="Maximum/Minimum/Average Number of Downloads of Plugins", label="tab:maxminavg_downloads")

save_latex(latex_max_min_avg_num_downloads, "max_min_avg_num_downloads")
print(latex_max_min_avg_num_downloads)

#Same with active installations
max_min_avg_active_installations = con.sql("""
                      SELECT MAX(active_installations) as MAX_INSTALLATIONS, MIN(active_installations) as MIN_INSTALLATIONS, ceil(AVG(active_installations)) as AVG_INSTALLATIONS
                      FROM plugins;
                      """).to_df()

latex_max_min_avg_active_installations = max_min_avg_active_installations.to_latex(index=False, caption="Maximum/Minimum/Average Number of Active Installations of Plugins", label="tab:maxminavg_active_installations")
save_latex(latex_max_min_avg_active_installations, "max_min_avg_active_installations")
    
print(max_min_avg_active_installations)
#Count Semgrep findings per rule
count_findings = con.sql("""
                         (SELECT rule_id, COUNT(*) AS "Number of Findings"
                         FROM findings_semgrep 
                         GROUP BY rule_id 
                         ORDER BY "Number of Findings" DESC)
                         UNION
                         ((SELECT rule_id, 0 from rules) 
                         EXCEPT
                        (SELECT rule_id, 0
                         FROM findings_semgrep
                         GROUP BY rule_id))
                         ORDER BY "Number of Findings" DESC;
                         """).to_df()

latex_count_findings = count_findings.to_latex(index=False, caption="Number of Findings per Semgrep Rule", label="tab:count_findings")

save_latex(latex_count_findings, "count_findings")

#Query which plugins have encountered a rule e.g WP-DEBUG-LOG_enabling this can be adapted to each rule
plugins_with_enabling = con.sql("""
                                SELECT plugin_slug, rule_id, num_downloads
                                FROM semgrep_runs s 
                                JOIN findings_semgrep f ON f.run_id = s.run_id
                                JOIN plugins p ON s.plugin_slug = p.slug
                                WHERE rule_id = 'WP-DEBUG-LOG_enabling' OR rule_id = 'WP-DEBUG_enabling'
                                ORDER BY num_downloads DESC;
                                """).to_df()
print(plugins_with_enabling)
latex_with_enabling = plugins_with_enabling.to_latex(index=False, caption="Plugins with Findings for WP-DEBUG-LOG_enabling or WP-DEBUG_enabling", label="tab:plugins_with_enabling")
save_latex(latex_with_enabling, "plugins_with_enabling")

print(count_findings)
#How many plugins encountered some kind of semgrep error -> Seems to all be 
error_count = con.sql("""
                      SELECT COUNT(*) as num_of_plugins_with_error, avg(error_count) FROM semgrep_runs WHERE error_count > 0;
                      """).to_df()

errors_not_type_3 = con.sql("""
                        SELECT errors FROM semgrep_runs WHERE error_count > 0 and errors NOT LIKE '%3%';
                        """).to_df()
print(error_count)

"""
LOG FILE NAME Analysis:
Using LIKE
Interesting Rules are file-put-contents_
fwrite_with-fopen
file-put-contents_log-file-var-assignment
fopen_var-assignment
"""
total_findings = con.sql("""
                         SELECT count(*)
                         FROM findings_semgrep 
                         WHERE rule_id = 'file-put-contents_';
                         """).fetchone()[0]
error_in_log_name = con.sql("""
                            SELECT count(lines) 

                            FROM findings_semgrep  
                            WHERE (lines 
                            LIKE '%file_put_contents(%error%,%'  OR  lines LIKE '%file_put_contents(%fail%,%'
                            OR lines LIKE '%file_put_contents(%exception%,%' 
                            OR lines LIKE '%file_put_contents(%fatal%,%' )
                            AND rule_id = 'file-put-contents_';
                            """).fetchone()[0]

debug_in_log_name = con.sql("""
                            SELECT count(lines) 
                            FROM findings_semgrep  
                            WHERE (lines 
                            LIKE '%file_put_contents(%debug%,%' 
                            OR lines LIKE '%file_put_contents(%dev%,%'
                            OR lines LIKE '%file_put_contents(%trace%,%'  
                            OR lines LIKE '%file_put_contents(%verbose%,%' 
                            OR lines LIKE '%file_put_contents(%diagnostic%,%' 
                            )
                            AND rule_id = 'file-put-contents_';
                            """).fetchone()[0]

#Others
#GROUP BY plugin names
'''
.htaccess , time() aber das nur bis zu einem gewissen grad, md5(), in tmp directory, date, sys_get_temp_dir()
Versuch zur Absicherung -> config
'''
securing_in_log_name = con.sql("""
    SELECT  count(lines)  
    FROM findings_semgrep  
    WHERE (
        lines SIMILAR TO '(?s).*file_put_contents\([^,]*htaccess\(.*'
        OR lines SIMILAR TO '(?s).*file_put_contents\([^,]*/tmp/\(.*'
        OR lines SIMILAR TO '(?s).*file_put_contents\([^,]*sys_get_temp_dir()\(.*'
        OR lines SIMILAR TO '(?s).*file_put_contents\([^,]*time\(.*'
        OR lines SIMILAR TO '(?s).*file_put_contents\([^,]*date\(.*'
        OR lines SIMILAR TO '(?s).*file_put_contents\([^,]*md5\(.*'
    )
    AND rule_id = 'file-put-contents_';
""").fetchone()[0]

htacess = con.sql("""
    SELECT  count(lines)  
    FROM findings_semgrep  
    WHERE (
        lines SIMILAR TO '(?s).*file_put_contents\(.*htaccess.*'
    )
    AND rule_id = 'file_put-contents_';
""").fetchone()[0]
names_from_a_variable = con.sql("""
    SELECT  count(lines)  
    FROM findings_semgrep  
    WHERE (
        lines SIMILAR TO '(?s).*file_put_contents\([^,\.]*\$.*'
    )
    AND rule_id = 'file-put-contents_';
""").fetchone()[0]

print(names_from_a_variable)


#Note the rest falls in to other names not tested will be classified as access, containes request business logic, installa logs
print(f"""
      Results for rule_id file-put-contents_ \n
      Total findings: {total_findings}
      Errors: {error_in_log_name}
      Debug: {debug_in_log_name}
      other: {total_findings - error_in_log_name - debug_in_log_name -htacess}
      securing: {securing_in_log_name}
      htaccess: {htacess}
      file_put_contents using a variable as handle: {names_from_a_variable}
      """)

#For semgrep category what was the plugin inside with max, min downloads and what is the avg
#____________________________________________________________#
#fwrite_with-fopen
#____________________________________________________________#
fwrite_with_fopen_total_findings = con.sql("""
                         SELECT count(*)
                         FROM findings_semgrep 
                         WHERE rule_id = 'fwrite_with-fopen';
                         """).fetchone()[0]

fwrite_with_fopen_from_variable = con.sql("""
    SELECT  count(lines)  
    FROM findings_semgrep  
    WHERE (
        lines SIMILAR TO '(?s).*fopen\(.?\$.*', 
    )
    AND rule_id = 'fwrite_with-fopen';
""").fetchone()[0]

fwrite_with_fopen_htacess = con.sql("""
    SELECT  count(lines)  
    FROM findings_semgrep  
    WHERE (
        lines SIMILAR TO '(?s).*fopen\(.*htaccess.*'
    )
    AND rule_id = 'fwrite_with-fopen';
""").fetchone()[0]

fwrite_with_fopen_debug = con.sql("""
    SELECT  count(lines)  
    FROM findings_semgrep  
    WHERE (
        lines SIMILAR TO '(?i).*fopen\(.*debug(?s).*' or
        lines SIMILAR TO '(?i).*fopen\(.*dev(?s).*' or
        lines SIMILAR TO '(?i).*fopen\(.*trace(?s).*' or
        lines SIMILAR TO '(?i).*fopen\(.*verbose(?s).*' or
        lines SIMILAR TO '(?i).*fopen\(.*diagnostic(?s).*'
    )
    AND rule_id = 'fwrite_with-fopen';
""").fetchone()[0]

fwrite_with_fopen_error = con.sql("""
    SELECT  count(lines)  
    FROM findings_semgrep  
    WHERE (
        lines SIMILAR TO '(?i).*fopen\(.*error(?s).*'
        or lines SIMILAR TO '(?i).*fopen\(.*fail(?s).*'
        or lines SIMILAR TO '(?i).*fopen\(.*exception(?s).*'
        or lines SIMILAR TO '(?i).*fopen\(.*fatal(?s).*'
    )
    AND rule_id = 'fwrite_with-fopen';
""").fetchone()[0]

#without htacess
fwrite_with_fopen_securing_in_log_name = con.sql("""
    SELECT  count(lines)  
    FROM findings_semgrep  
    WHERE (
        lines SIMILAR TO '(?s).*fopen\([^,]*/tmp/\(.*'
        OR lines SIMILAR TO '(?s).*fopen\([^,]*sys_get_temp_dir()\(.*'
        OR lines SIMILAR TO '(?s).*fopen\([^,]*time\(.*'
        OR lines SIMILAR TO '(?s).*fopen\([^,]*date\(.*'
        OR lines SIMILAR TO '(?s).*fopen\([^,]*md5\(.*'
    )
    AND rule_id = 'fwrite_with-fopen';
""").fetchone()[0]

fwrite_with_fopen_other = fwrite_with_fopen_total_findings - fwrite_with_fopen_debug - fwrite_with_fopen_error - fwrite_with_fopen_htacess



print(f"""\nResults for fwrite_with-fopen \n
      Total finding: {fwrite_with_fopen_total_findings}
      Error logs : {fwrite_with_fopen_error}
      Debug logs : {fwrite_with_fopen_debug}
      Other logs: {fwrite_with_fopen_other}
      .htaccess writes: {fwrite_with_fopen_htacess}
      Some kind of securing in logname: {fwrite_with_fopen_securing_in_log_name} 
      fopen from a variable : {fwrite_with_fopen_from_variable}
      """)


#____________________________________________________________#
#file-put-contents_log-file-var-assignment
#____________________________________________________________#
#Write query such that first line is checked for debug/error
file_put_contents_log_file_var_assignment_total = con.sql("""
                         SELECT count(*)
                         FROM findings_semgrep 
                         WHERE rule_id = 'file-put-contents_log-file-var-assignment';
                         """).fetchone()[0]

file_put_contents_log_file_var_assignment_error = con.sql("""
    SELECT  count(lines)  
    FROM findings_semgrep  
    WHERE (
        lines SIMILAR TO '(?i).*error(?s).*'
        or lines SIMILAR TO '(?i).*fail(?s).*'
        or lines SIMILAR TO '(?i).*exception(?s).*'
        or lines SIMILAR TO '(?i).*fatal(?s).*'
    )
    AND rule_id = 'file-put-contents_log-file-var-assignment';
""").fetchone()[0]

file_put_contents_log_file_var_assignment_debug = con.sql("""
    SELECT  count(lines)  
    FROM findings_semgrep  
    WHERE (
        lines SIMILAR TO '(?i).*debug(?s).*'
    )
    AND rule_id = 'file-put-contents_log-file-var-assignment';
""").fetchone()[0]

file_put_contents_log_file_var_assignment_htacess = con.sql("""
    SELECT  count(lines)  
    FROM findings_semgrep  
    WHERE (
        lines SIMILAR TO '.*htaccess(?s).*'
    )
    AND rule_id = 'file-put-contents_log-file-var-assignment';
""").fetchone()[0]

#All results are with date for this one
file_put_contents_log_file_var_assignment_securing_in_log_name = con.sql("""
    SELECT  count(lines)  
    FROM findings_semgrep  
    WHERE (
        lines SIMILAR TO '.*/tmp/(?s).*'
        OR lines SIMILAR TO '.*sys_get_temp_dir\((?s).*'
        OR lines SIMILAR TO '.*time\((?s).*'
        OR lines SIMILAR TO '.*date\((?s).*'
        OR lines SIMILAR TO '.*md5\((?s).*'
    )
    AND rule_id = 'file-put-contents_log-file-var-assignment';
""").fetchone()[0]

file_put_contents_log_file_var_assignment_variable_names = con.sql("""
    SELECT  count(lines)
    FROM findings_semgrep  
    WHERE (
        lines SIMILAR TO '.*\$.*=.*\$(?s).*'
    )
    AND rule_id = 'file-put-contents_log-file-var-assignment';
""").fetchone()[0]

file_put_contents_log_file_var_assignment_access = file_put_contents_log_file_var_assignment_total - file_put_contents_log_file_var_assignment_error - file_put_contents_log_file_var_assignment_error - file_put_contents_log_file_var_assignment_htacess

print(f"""
Results for file_put_contents_log_file_var_assignment
      Total findings: {file_put_contents_log_file_var_assignment_total}
      Errors: {file_put_contents_log_file_var_assignment_error}
      Debug: {file_put_contents_log_file_var_assignment_debug}
      Access: {file_put_contents_log_file_var_assignment_access}
      securing: {file_put_contents_log_file_var_assignment_securing_in_log_name}
      Variable created from another variable: {file_put_contents_log_file_var_assignment_variable_names}
      """)

#____________________________________________________________#
#fopen_var-assignment
#____________________________________________________________#
fopen_var_assignment_total = con.sql("""
                         SELECT count(*)
                         FROM findings_semgrep 
                         WHERE rule_id = 'fopen_var-assignment';
                         """).fetchone()[0]

fopen_var_assignment_error = con.sql("""
    SELECT  count(lines)  
    FROM findings_semgrep  
    WHERE (
        lines SIMILAR TO '(?i).*error(?s).*'
        or lines SIMILAR TO '(?i).*fail(?s).*'
        or lines SIMILAR TO '(?i).*exception(?s).*'
        or lines SIMILAR TO '(?i).*fatal(?s).*'
    )
    AND rule_id = 'fopen_var-assignment';
""").fetchone()[0]

fopen_var_assignment_debug = con.sql("""
    SELECT  count(lines)  
    FROM findings_semgrep  
    WHERE (
        lines SIMILAR TO '(?i).*debug(?s).*'
        or lines SIMILAR TO '(?i).*dev(?s).*'
        or lines SIMILAR TO '(?i).*trace(?s).*'
        or lines SIMILAR TO '(?i).*verbose(?s).*'
        or lines SIMILAR TO '(?i).*diagnostic(?s).*'
    )
    AND rule_id = 'fopen_var-assignment';
""").fetchone()[0]

fopen_var_assignment_securing_in_log_name = con.sql("""
    SELECT  count(lines)  
    FROM findings_semgrep  
    WHERE (
        lines SIMILAR TO '(?s).*fopen\([^,]*/tmp/\(.*'
        OR lines SIMILAR TO '(?s).*fopen\([^,]*sys_get_temp_dir()\(.*'
        OR lines SIMILAR TO '(?s).*fopen\([^,]*time\(.*'
        OR lines SIMILAR TO '(?s).*fopen\([^,]*date\(.*'
        OR lines SIMILAR TO '(?s).*fopen\([^,]*md5\(.*'
    )
    AND rule_id = 'fopen_var-assignment';
""").fetchone()[0]

fopen_var_assignment_htacess = con.sql("""
    SELECT  count(lines)  
    FROM findings_semgrep  
    WHERE (
        lines SIMILAR TO '(?i).*htaccess(?s).*'
    )
    AND rule_id = 'fopen_var-assignment';
""").fetchone()[0]

fopen_var_assignment_file_var_assignment = con.sql("""
    SELECT  count(lines)
    FROM findings_semgrep  
    WHERE (
        lines SIMILAR TO '.*\$.*=.*\$(?s).*'
    )
    AND rule_id = 'fopen_var-assignment';
""").fetchone()[0]
#securing in log name

fopen_var_assignment_access = fopen_var_assignment_total - fopen_var_assignment_debug - fopen_var_assignment_error - fopen_var_assignment_htacess

print(f"""
Results for fopen_var-assignment
      Total findings: {fopen_var_assignment_total}
      Errors: {fopen_var_assignment_error}
      Debug: {fopen_var_assignment_debug}
      Access: {fopen_var_assignment_access}
      .htaccess writes: {fopen_var_assignment_htacess}
      """)


#____________________________________________________________#
#fputs_with-fopen
#____________________________________________________________#

#0 findings nothing to do.

#####################################################
#Dynamic Analysis####################################
#####################################################
approximate_of_wp_cli_in_seconds = 60 #30 sec sleep, 30 download and unzip plugin/ install wordpress and activate plugin as well as cli commands

sum_table_dynamic_analysis = con.sql(f"""
            SELECT   sum(num_rest_endpoints_called) as "total restendpoints", 
            sum(num_rest_endpoints_http_ok) as "total http OK",
            sum(num_rest_endpoints_http_ok) / sum(num_rest_endpoints_called) as "success quote REST",
            sum(num_ajax_endpoints_called) as "total ajax endpoints",
            sum(num_ajax_endpoints_http_ok) as "total ajax httpok",
            sum(num_ajax_endpoints_http_ok) / sum(num_ajax_endpoints_called) as "success quote AJAX",
            sum(time_spend) + count(*) * {approximate_of_wp_cli_in_seconds} as "total time spend"
            FROM dynamic_analysis;
                                     """).to_df()

latex_sum_table_dynamic_analysis = sum_table_dynamic_analysis.to_latex(index=False, caption="Summary of Dynamic Analysis Results", label="tab:sum_dynamic_analysis")
save_latex(latex_sum_table_dynamic_analysis, "sum_table_dynamic_analysis")
print(sum_table_dynamic_analysis)

con.sql("""
        CREATE OR REPLACE VIEW distinct_path AS
        select DISTINCT params from findings_function_hooks WHERE params LIKE '%log%' AND params not LIKE '%logo%' AND params not LIKE '%login%' AND params not LIKE '%logged%'
    AND params not LIKE '%blog%' AND params not LIKE '%dialog%' 
    AND params not LIKE '%.php]' AND params not LIKE '%.html%' 
    AND params not LIKE '%.pid%' AND params NOT LIKE '%benchmark-log-plugin%' 
    AND params not LIKE '%.css%' AND params not LIKE '%.js%'
    AND params not LIKE '%monolog%';
        """)

number_of_filenames_used_that_contained_logs = con.sql(
    """
    select COUNT(params) as "Num of filepaths containing log", COUNT(DISTINCT params) as "Num of distinct filepaths containing logs" from findings_function_hooks WHERE params LIKE '%log%' AND params not LIKE '%logo%' AND params not LIKE '%login%' AND params not LIKE '%logged%'
    AND params not LIKE '%blog%' AND params not LIKE '%dialog%' 
    AND params not LIKE '%.php]' AND params not LIKE '%.html%' 
    AND params not LIKE '%.pid%' AND params NOT LIKE '%benchmark-log-plugin%' 
    AND params not LIKE '%.css%' AND params not LIKE '%.js%'
    AND params not LIKE '%monolog%';
    """
)

number_of_filenames_used_that_contained_logs_group_by_slug = con.sql("""
        select COUNT(params) as "Num of filepaths containing log", COUNT(DISTINCT params) as "Num of distinct filepaths containing logs" from findings_function_hooks WHERE params LIKE '%log%' AND params not LIKE '%logo%' AND params not LIKE '%login%' AND params not LIKE '%logged%'
      AND params not LIKE '%blog%' AND params not LIKE '%dialog%' 
      AND params not LIKE '%.php]' AND params not LIKE '%.html%' 
      AND params not LIKE '%.pid%' AND params NOT LIKE '%benchmark-log-plugin%' 
      AND params not LIKE '%.css%' AND params not LIKE '%.js%'
      AND params not LIKE '%monolog%' GROUP BY plugin_slug;
        """)

grouped_log_names = con.sql(
    """
    select params as filepath , count(params) as num_of_times
    from findings_function_hooks 
    WHERE params LIKE '%log%' AND params not LIKE '%logo%' AND params not LIKE '%login%' AND params not LIKE '%logged%'
    AND params not LIKE '%blog%' AND params not LIKE '%dialog%' 
    AND params not LIKE '%.php]' AND params not LIKE '%.html%' 
    AND params not LIKE '%.pid%' AND params NOT LIKE '%benchmark-log-plugin%' 
    AND params not LIKE '%.css%' AND params not LIKE '%.js%'
    AND params not LIKE '%monolog%'
    GROUP BY params
    ORDER BY num_of_times DESC;
    """
).to_df()
print(grouped_log_names.to_string())

general_function_hooking_info = con.sql(
    """
    SELECT COUNT(DISTINCT function) AS "distinct functions hooked",
            COUNT(DISTINCT params) AS "distinct filepath used",
            COUNT(*) AS "total function hooks"
    FROM findings_function_hooks;
    """).to_df()

functions_used_with_dynamic_tests = con.sql(
    """
    SELECT function, count(*) as "total called"
    FROM findings_function_hooks
    GROUP BY function
    ORDER BY "total called" DESC;
    """
).to_df()

latex_functions_used_with_dynamic_tests = functions_used_with_dynamic_tests.to_latex(index=False, caption="Functions Called in Dynamic Analysis Tests", label="tab:functions_used_dynamic_tests")
save_latex(latex_functions_used_with_dynamic_tests, "functions_used_dynamic_tests")
print(functions_used_with_dynamic_tests)

distinct_path_containing_error = con.sql(
    """
    SELECT *
    FROM distinct_path
    WHERE params SIMILAR TO '(?i).*error.*';
    """
).to_df().to_string()

distinct_path_containing_debug = con.sql(
    """
    SELECT *
    FROM distinct_path
    WHERE params SIMILAR TO '(?i).*debug.*';
    """
).to_df().to_string()

print(distinct_path_containing_error)
print(distinct_path_containing_debug)

##########################################################
################# findings_wp_cli ########################
##########################################################
findings_wp_cli_containing_logs = con.sql(
    """
    select plugin_slug, name_of_changed_file
    from findings_wp_cli 
    where name_of_changed_file similar to  '(?si).*log.*'
    AND name_of_changed_file NOT LIKE '%.htaccess'
    AND name_of_changed_file NOT LIKE '%.php'
    AND name_of_changed_file NOT LIKE '%.png'
    AND name_of_changed_file NOT LIKE '%.svg'
    AND name_of_changed_file NOT LIKE '%.jpg'
    AND name_of_changed_file NOT LIKE '%.scss'
    AND name_of_changed_file NOT LIKE '%.js'
    AND name_of_changed_file NOT LIKE '%.html'
    AND name_of_changed_file NOT LIKE '%.css'
    AND name_of_changed_file NOT LIKE '%.webp'
    AND name_of_changed_file NOT LIKE '%CHANGELOG%'
    ;
    """
).to_df().to_string() #php raus?
#Look at last zip file number is log is contained multiple times

print(findings_wp_cli_containing_logs)

findings_wp_cli_containing_logs_group_slug = con.sql(
    """
    select plugin_slug, count(*) as num_of_files
    from findings_wp_cli 
    where name_of_changed_file similar to  '(?si).*log.*'
    AND name_of_changed_file NOT LIKE '%.htaccess'
    AND name_of_changed_file NOT LIKE '%.php'
    AND name_of_changed_file NOT LIKE '%.png'
    AND name_of_changed_file NOT LIKE '%.svg'
    AND name_of_changed_file NOT LIKE '%.jpg'
    AND name_of_changed_file NOT LIKE '%.scss'
    AND name_of_changed_file NOT LIKE '%.js'
    AND name_of_changed_file NOT LIKE '%.html'
    AND name_of_changed_file NOT LIKE '%.css'
    AND name_of_changed_file NOT LIKE '%.webp'
    AND name_of_changed_file NOT LIKE '%CHANGELOG%'
    GROUP BY plugin_slug
    ORDER BY num_of_files DESC
    ;
    """
).to_df()

findings_wp_cli_group_filename = con.sql(
    """
    select name_of_changed_file, count(*) as num_of_times
    from findings_wp_cli
    where name_of_changed_file similar to  '(?si).*log.*'
     AND name_of_changed_file NOT LIKE '%.htaccess'
    AND name_of_changed_file NOT LIKE '%.htaccess'
    AND name_of_changed_file NOT LIKE '%.php'
    AND name_of_changed_file NOT LIKE '%.png'
    AND name_of_changed_file NOT LIKE '%.svg'
    AND name_of_changed_file NOT LIKE '%.jpg'
    AND name_of_changed_file NOT LIKE '%.scss'
    AND name_of_changed_file NOT LIKE '%.js'
    AND name_of_changed_file NOT LIKE '%.html'
    AND name_of_changed_file NOT LIKE '%.css'
    AND name_of_changed_file NOT LIKE '%.webp'
    AND name_of_changed_file NOT LIKE '%CHANGELOG%'
    GROUP BY name_of_changed_file
    ORDER BY num_of_times DESC
    ;
    """
).to_df()

latex_findings_wp_cli_group_filename = findings_wp_cli_group_filename.to_latex(index=False, caption="Log File Names Found in WP-CLI Dynamic Analysis", label="tab:findings_wp_cli_log_filenames")
save_latex(latex_findings_wp_cli_group_filename, "findings_wp_cli_log_filenames")
print(latex_findings_wp_cli_group_filename)
##########################################################
################# findings_rest ##########################
##########################################################
#TODO: Query plugins DESC, type of operation, also AJAX and WP-CLI
findings_rest_count = con.sql(
    """
    select COUNT(*) as num_of_findings
    from findings_rest;
    """
).to_df()
print(findings_rest_count)

findings_rest_containing_logs_count = con.sql(
    """
    select COUNT(*) as num_of_findings
    from findings_rest
    where name_of_changed_file similar to  '(?si).*log.*'
    AND name_of_changed_file NOT LIKE '%.htaccess'
    AND name_of_changed_file NOT LIKE '%.php'
    AND name_of_changed_file NOT LIKE '%.png'
    AND name_of_changed_file NOT LIKE '%.svg'
    AND name_of_changed_file NOT LIKE '%.jpg'
    AND name_of_changed_file NOT LIKE '%.scss'
    AND name_of_changed_file NOT LIKE '%.js'
    AND name_of_changed_file NOT LIKE '%.html'
    AND name_of_changed_file NOT LIKE '%.css'
    AND name_of_changed_file NOT LIKE '%CHANGELOG%'
    ;
    """
).to_df()
print(findings_rest_containing_logs_count)

findings_rest_containing_logs = con.sql(
    """
    select name_of_changed_file, count(*) as num_of_times
    from findings_rest 
    where name_of_changed_file similar to  '(?si).*log.*'
    AND name_of_changed_file NOT LIKE '%.htaccess'
    AND name_of_changed_file NOT LIKE '%.php'
    AND name_of_changed_file NOT LIKE '%.png'
    AND name_of_changed_file NOT LIKE '%.svg'
    AND name_of_changed_file NOT LIKE '%.jpg'
    AND name_of_changed_file NOT LIKE '%.scss'
    AND name_of_changed_file NOT LIKE '%.js'
    AND name_of_changed_file NOT LIKE '%.html'
    AND name_of_changed_file NOT LIKE '%.css'
    AND name_of_changed_file NOT LIKE '%CHANGELOG%'
    GROUP BY name_of_changed_file
    ORDER BY num_of_times DESC
    ;
    """
).to_df().to_string() #php raus?


findings_rest_num_of_debug_logs = con.sql(
    """
    select count(DISTINCT name_of_changed_file) as "num_of_debug_logs"
    from findings_rest 
    where name_of_changed_file similar to  '(?si).*log.*'
    AND name_of_changed_file NOT LIKE '%.htaccess'
    AND name_of_changed_file NOT LIKE '%.php'
    AND name_of_changed_file NOT LIKE '%.png'
    AND name_of_changed_file NOT LIKE '%.svg'
    AND name_of_changed_file NOT LIKE '%.jpg'
    AND name_of_changed_file NOT LIKE '%.scss'
    AND name_of_changed_file NOT LIKE '%.js'
    AND name_of_changed_file NOT LIKE '%.html'
    AND name_of_changed_file NOT LIKE '%.css'
    AND name_of_changed_file NOT LIKE '%CHANGELOG%'
    AND name_of_changed_file SIMILAR TO '(?i).*debug.*'
    ;
    """
).to_df().to_string()
#Create View and look for debug, error
print(findings_rest_containing_logs)

findings_rest_num_of_error_logs = con.sql(
    """
    select count(DISTINCT name_of_changed_file) as "num_of_debug_logs"
    from findings_rest 
    where name_of_changed_file similar to  '(?si).*log.*'
    AND name_of_changed_file NOT LIKE '%.htaccess'
    AND name_of_changed_file NOT LIKE '%.php'
    AND name_of_changed_file NOT LIKE '%.png'
    AND name_of_changed_file NOT LIKE '%.svg'
    AND name_of_changed_file NOT LIKE '%.jpg'
    AND name_of_changed_file NOT LIKE '%.scss'
    AND name_of_changed_file NOT LIKE '%.js'
    AND name_of_changed_file NOT LIKE '%.html'
    AND name_of_changed_file NOT LIKE '%.css'
    AND name_of_changed_file NOT LIKE '%CHANGELOG%'
    AND name_of_changed_file SIMILAR TO '(?i).*error.*'
    ;
    """
).to_df().to_string()

##########################################################
################# findings_ajax ##########################
##########################################################
findings_ajax_containing_logs = con.sql(
    """
    select  DISTINCT name_of_changed_file
    from findings_ajax 
    where name_of_changed_file similar to  '(?si).*log.*'
    AND name_of_changed_file NOT LIKE '%.htaccess'
    AND name_of_changed_file NOT LIKE '%.php'
    AND name_of_changed_file NOT LIKE '%.png'
    AND name_of_changed_file NOT LIKE '%.svg'
    AND name_of_changed_file NOT LIKE '%.jpg'
    AND name_of_changed_file NOT LIKE '%.scss'
    AND name_of_changed_file NOT LIKE '%.js'
    AND name_of_changed_file NOT LIKE '%.html'
    AND name_of_changed_file NOT LIKE '%.css'
    AND name_of_changed_file NOT LIKE '%CHANGELOG%'
    AND name_of_changed_file NOT LIKE '%temp-write-test%'
    ;
    """
).to_df().to_string() #php raus?

print(findings_ajax_containing_logs)

findings_ajax_containing_just_some_filtering = con.sql(
    """
    select  DISTINCT name_of_changed_file
    from findings_ajax 
    where  name_of_changed_file similar to  '(?si).*log.*'
    AND name_of_changed_file NOT LIKE '%.htaccess'
    AND name_of_changed_file NOT LIKE '%.php'
    AND name_of_changed_file NOT LIKE '%.png'
    AND name_of_changed_file NOT LIKE '%.svg'
    AND name_of_changed_file NOT LIKE '%.jpg'
    AND name_of_changed_file NOT LIKE '%.scss'
    AND name_of_changed_file NOT LIKE '%.js'
    AND name_of_changed_file NOT LIKE '%.html'
    AND name_of_changed_file NOT LIKE '%.css'
    AND name_of_changed_file NOT LIKE '%temp-write-test%'
    AND name_of_changed_file NOT LIKE '%CHANGELOG%'
    ;
    """
).to_df().to_string() #php raus?

print(findings_ajax_containing_just_some_filtering)

