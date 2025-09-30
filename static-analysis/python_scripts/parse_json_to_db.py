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
        
    
    #Save run
    con.sql("""
            INSERT INTO semgrep_runs (run_id, plugin_name, plugin_slug, plugin_version, plugin_download_link, plugin_num_dowloads, active_installations, error_count, errors) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, params = (i, name, info_data.get("slug"), version, download_link, num_downloads, active_installations, error_count, json.dumps(errors if errors else None)))

    results = semgrep_data.get("results") #semgrep results/ each run can have multiple findings
    
    #save findings
    for result in results:
        rule_id = result.get("check_id")
        file_path = result.get("path")
        run_id = i
        start_line = result.get("start").get("line")
        end_line = result.get("end").get("line")
        message = result.get("extra").get("message")
        lines = result.get("extra").get("lines")
        
        con.sql("""
                INSERT INTO findings (run_id, rule_id, file_path, start_line, end_line, message, lines) VALUES (?, ?, ?, ?, ?, ?, ?);
                """, params = (run_id, rule_id, file_path, start_line, end_line, message, lines))
    
    
con.close()