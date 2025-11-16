import sys
import os
import json
import duckdb

if len(sys.argv) != 2:
    print("Usage: python parse_json_to_db.py <path_to_result_directory>")
    sys.exit(1)

result_dir = sys.argv[1]

if not os.path.exists(result_dir):
    print(f"Error: The directory {result_dir} does not exist.")
    sys.exit(1)

con = duckdb.connect('semgrep_analysis.db')
con.execute("PRAGMA threads=4;")

slugs = [dir for dir in os.listdir(result_dir)]

print(f"Found {len(slugs)} directories to process.")

for i, slug in enumerate(slugs):
    info_path = os.path.join(result_dir, slug, "info.json")
    
    ##################RESULTS PARSING##################
    semgrep_path = os.path.join(result_dir, slug, "semgrep.json")
    with open(semgrep_path, 'r') as f:
        semgrep_data = json.load(f)
        error_count = len(semgrep_data.get("errors"))
        errors = semgrep_data.get("errors") if semgrep_data.get("errors") != [] else None

    with open(info_path, 'r') as f:
        info_data = json.load(f)
        name = info_data.get("Name")
        version = info_data.get("version")
        download_link = info_data.get("download_link")
        num_downloads = int(info_data.get("Downloads").replace(',', ''))
        active_installations = int(info_data.get("Active Installs").replace(',', ''))
        
    #Save plugin info
    con.sql("""
            INSERT OR IGNORE INTO plugins (name, slug, version, download_link, num_downloads, active_installations) VALUES (?, ?, ?, ?, ?, ?);
            """, params = (name, info_data.get("slug"), version, download_link, num_downloads, active_installations))
    #Save run
    con.sql("""
            INSERT INTO semgrep_runs (run_id, plugin_slug, error_count, errors) VALUES (?, ?, ?, ?);
            """, params = (i, info_data.get("slug"), error_count, json.dumps(errors if errors else None)))

    results = semgrep_data.get("results") #semgrep results/ each run can have multiple findings
    
    #save findings
    for result in results:
        rule_id = result.get("check_id")
        file_path = result.get("path").replace("plugins/", "")
        run_id = i
        start_line = result.get("start").get("line")
        end_line = result.get("end").get("line")
        message = result.get("extra").get("message")
        lines = result.get("extra").get("lines")
        
        con.sql("""
                INSERT INTO findings_semgrep (run_id, rule_id, file_path, start_line, end_line, message, lines) VALUES (?, ?, ?, ?, ?, ?, ?);
                """, params = (run_id, rule_id, file_path, start_line, end_line, message, lines))
    
    ####################JUST AJAX FINDINGS PARSING####################
    ##Closure
    ajax_closure_path = os.path.join(result_dir, slug, "ajax_closure.json")
    
    
    with open(ajax_closure_path, 'r') as f:
        ajax_closure_data = json.load(f)
    
    for ajax_route in ajax_closure_data:
        priv = ajax_route.get("priv")
        action = ajax_route.get("action")
        result = con.sql("""
                INSERT INTO ajax_routes (plugin_slug, action, priv) VALUES (?, ?, ?)
                RETURNING route_id
                """, params= (slug, action, priv)).fetchone()
        args = ajax_route.get("args")
        route_id = result[0]
        for method_arg in args:
            con.sql("""
                    INSERT INTO ajax_route_arguments (route_id, method, arg_name) VALUES (?,?,?)
                    """, params=(route_id, method_arg[0], method_arg[1]))
            
    
        
    
    # ajax_findings_dir = os.path.join(result_dir, slug, "ajax-findings")
    
    # for finding in os.listdir(ajax_findings_dir):
    #     pass
    # ajax_findings = ajax_findings_data.get("results")
    
    # for ajax_finding in ajax_findings:
    #     extra = ajax_finding.get("extra")
    #     metavars = extra.get("metavars")
        
    
    ################END RESULTS PARSING##################
    
    
    
con.close()