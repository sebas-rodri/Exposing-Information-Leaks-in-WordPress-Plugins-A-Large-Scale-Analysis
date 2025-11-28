import duckdb
import os
import json
from baseline_paths import BASELINE_PATHS
DB_NAME = "/results.db"

def parse_jsonl(slug):
    try:
        con = duckdb.connect(DB_NAME)
        with open("/shared/dynamic_test_findings.jsonl", "r") as file:
            json_list = list(file)
        for finding in json_list:
            finding = json.loads(finding)
            interface = finding.get("interface")
            method = finding.get("method")
            url = finding.get("url") # In case of WP-CLI this is the command
            if interface != "WP_CLI":
                url = finding.get("url").strip("http://localhost:8080")
            data = finding.get("data")
            name_of_changed_file = finding.get("name_of_changed_file")
            type_of_operation = finding.get("type_of_operation")
            zip_counter = finding.get("zip_counter")
            if interface == "REST":
                con.sql("""
                        INSERT INTO findings_rest (plugin_slug, url, http_method, data, name_of_changed_file, type_of_operation, zip_file_number)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, params= (slug, url, method, data, name_of_changed_file, type_of_operation, zip_counter))
            elif interface == "AJAX":
                con.sql("""
                        INSERT INTO findings_ajax (plugin_slug, url, http_method, data, name_of_changed_file, type_of_operation, zip_file_number)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, params= (slug, url, method, data, name_of_changed_file, type_of_operation, zip_counter))
            elif interface == "WP_CLI":
                con.sql("""
                        INSERT INTO findings_wp_cli (plugin_slug, command, name_of_changed_file, type_of_operation, zip_file_number)
                        VALUES (?, ?, ?, ?, ?)
                        """, params= (slug, url, name_of_changed_file, type_of_operation, zip_counter))
                
        con.close()
            
    except Exception as e:
        print(f"Error parsing /shared/dynamic_test_findings.jsonl findings, Exceptions: {e}")

def save_analysis_metrics(slug, num_unique_rest_endpoints, num_rest_endpoints_called, num_rest_endpoints_http_ok, num_ajax_endpoints, num_ajax_endpoints_called, num_ajax_endpoints_http_ok, time_spend):
    try:
        con = duckdb.connect(DB_NAME)
        con.sql("""
                INSERT INTO dynamic_analysis 
                (plugin_slug, num_unique_rest_endpoints, num_rest_endpoints_called, num_rest_endpoints_http_ok, num_ajax_endpoints, num_ajax_endpoints_called, num_ajax_endpoints_http_ok, time_spend)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, params=(slug, num_unique_rest_endpoints, num_rest_endpoints_called, num_rest_endpoints_http_ok, num_ajax_endpoints, num_ajax_endpoints_called, num_ajax_endpoints_http_ok, time_spend))
        con.close()
    except Exception as e:
        print(f"Error saving metrics of dynamic Analisys for plugin {slug} Exception: {e}")
        
def save_function_hooking_results(slug):
    try:
        con = duckdb.connect(DB_NAME)
        with open("shared-wordpress/function-hooking.json", "r") as f:
            json_list = list(f)
        for jsonl in json_list:
            finding = json.loads(jsonl)
            parameters = finding.get("params")
            if parameters[0] in BASELINE_PATHS:
                continue #Path was in baseline when runnign with no plugins
            function = finding.get("function")
            error = finding.get("error")
            try:
                con.sql("""
                INSERT INTO findings_function_hooks
                (plugin_slug, function, params, error)
                VALUES (?, ?, ?, ?)
                """, params=(slug, function, parameters, error))
            except Exception as e:
                print(f"Error inserting into findings_wp_cli {e}")
        con.close()
    except Exception as e:
        print(f"Error saving function-hooking.json {e}")