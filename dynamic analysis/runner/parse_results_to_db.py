import duckdb
import os
import json

DB_NAME = "results.db"

def parse_jsonl(slug):
    try:
        con = duckdb.connect(DB_NAME)
        with open("/shared/dynamic_test_findings.jsonl", "r") as file:
            json_list = list(file)
        for finding in json_list:
            finding = json.loads(finding)
            interface = finding.get("interface")
            method = finding.get("method")
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
            else: #AJAX
                con.sql("""
                        INSERT INTO findings_ajax (plugin_slug, url, http_method, data, name_of_changed_file, type_of_operation, zip_file_number)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, params= (slug, url, method, data, name_of_changed_file, type_of_operation, zip_counter))
        con.close()
            
    except Exception as e:
        print(f"Error parsing /shared/dynamic_test_findings.jsonl findings, Exceptions: {e}")

def save_analysis_metrics(slug, num_unique_rest_endpoints, num_rest_endpoints_called, num_rest_endpoints_http_ok, num_rest_endpoints_http_other, num_ajax_endpoints, num_ajac_endpoints_called, time_spend):
    try:
        con = duckdb.connect(DB_NAME)
        con.sql("""
                INSERT INTO dynamic_analysis 
                (plugin_slug, num_unique_rest_endpoints, num_rest_endpoints_called, num_rest_endpoints_http_ok, num_rest_endpoints_http_other, num_ajax_endpoints, num_ajac_endpoints_called, time_spend)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, params=(slug, num_unique_rest_endpoints, num_rest_endpoints_called, num_rest_endpoints_http_ok, num_rest_endpoints_http_other, num_ajax_endpoints, num_ajac_endpoints_called, time_spend))
        con.close()
    except Exception as e:
        print(f"Error saving metrics of dynamic Analisys for plugin {slug} Exception: {e}")