import duckdb
import sys

if len(sys.argv) != 2:
    print("Usage: python create_duckdb.py dbname")
    sys.exit(1)

con = duckdb.connect(sys.argv[1])

#Sequences for PRIMARY KEY
con.sql("""
        CREATE SEQUENCE IF NOT EXISTS run_ids START 1;
        CREATE SEQUENCE IF NOT EXISTS finding_ids START 1;
        CREATE SEQUENCE IF NOT EXISTS dynamic_analysis_ids START 1;
        CREATE SEQUENCE IF NOT EXISTS rest_finding_ids START 1;
        CREATE SEQUENCE IF NOT EXISTS ajax_findings_ids START 1;
        CREATE SEQUENCE IF NOT EXISTS ajax_routes_ids START 1;
        """)

#Create Tables
con.sql("""
        CREATE TABLE IF NOT EXISTS plugins (
            name VARCHAR NOT NULL,
            slug VARCHAR NOT NULL UNIQUE,
            version VARCHAR NOT NULL,
            download_link VARCHAR NOT NULL,
            num_downloads INTEGER NOT NULL,
            active_installations INTEGER NOT NULL,
            PRIMARY KEY (slug)
            );
        
        CREATE TABLE IF NOT EXISTS dynamic_analysis(
            plugin_slug VARCHAR NOT NULL PRIMARY KEY,
            num_unique_rest_endpoints INTEGER NOT NULL,
            num_rest_enpoints_called INTEGER NOT NULL,
            num_rest_endpoints_http_ok INTEGER NOT NULL,
            num_rest_endpoints_http_other INTEGER GENERATED ALWAYS AS (num_rest_enpoints_called - num_rest_endpoints_http_ok) VIRTUAL,
            num_ajax_endpoints INTEGER NOT NULL,
            num_ajax_endpoints_called INTEGER NOT NULL,
            FOREIGN KEY (plugin_slug) REFERENCES plugins (slug)
            );
            
        CREATE TABLE IF NOT EXISTS ajax_routes (
            route_id INTEGER DEFAULT(nextval('ajax_routes_ids')) PRIMARY KEY,
            plugin_slug VARCHAR NOT NULL,
            action VARCHAR NOT NULL,
            priv BOOLEAN NOT NULL,
            FOREIGN KEY (plugin_slug) REFERENCES plugins (slug)
        );
        
        CREATE TABLE IF NOT EXISTS ajax_route_arguments (
            route_id INTEGER NOT NULL,
            method VARCHAR NOT NULL, -- POST/GET etc.
            arg_name VARCHAR NOT NULL,
            PRIMARY KEY (route_id, method, arg_name),
            FOREIGN KEY (route_id) REFERENCES ajax_routes (route_id)
            
        );
            
        CREATE TABLE IF NOT EXISTS semgrep_runs (
            run_id INTEGER DEFAULT(nextval('run_ids')) PRIMARY KEY,
            plugin_slug VARCHAR NOT NULL,
            error_count INTEGER NOT NULL,
            errors VARCHAR,
            FOREIGN KEY (plugin_slug) REFERENCES plugins (slug)
            );
        
        CREATE TABLE IF NOT EXISTS rules (
            rule_id VARCHAR NOT NUll PRIMARY KEY,
            severity VARCHAR NOT NULL CHECK(severity IN ['INFO', 'ERROR', 'WARNING']),
            sink VARCHAR
        );
        CREATE TABLE IF NOT EXISTS findings_semgrep (
            finding_id INTEGER DEFAULT(nextval('finding_ids')) PRIMARY KEY,
            run_id INTEGER NOT NULL,
            rule_id VARCHAR NOT NULL,
            file_path VARCHAR NOT NULL,
            start_line INTEGER NOT NULL,
            end_line INTEGER NOT NULL,
            message VARCHAR,
            lines VARCHAR,
            FOREIGN KEY (rule_id) REFERENCES rules (rule_id),
            FOREIGN KEY (run_id) REFERENCES semgrep_runs (run_id)
            );
            
            
        CREATE TABLE IF NOT EXISTS findings_rest(
                finding_id INTEGER DEFAULT(nextval('rest_finding_ids')) PRIMARY KEY,
                plugin_slug VARCHAR NOT NULL,
                url VARCHAR NOT NULL,
                http_method VARCHAR NOT NULL,
                data VARCHAR,
                name_of_changed_file VARCHAR,
                type_of_operation VARCHAR CHECK(type_of_operation IN ['create', 'modify', 'delete', 'move']),
                zip_file_number INTEGER NOT NULL,
                FOREIGN KEY (plugin_slug) REFERENCES dynamic_analysis (plugin_slug)
            );
            

        CREATE TABLE IF NOT EXISTS findings_ajax(
                finding_id INTEGER DEFAULT(nextval('ajax_findings_ids')) PRIMARY KEY,
                plugin_slug VARCHAR NOT NULL,
                url VARCHAR NOT NULL,
                http_method VARCHAR NOT NULL,
                data VARCHAR,
                name_of_changed_file VARCHAR,
                type_of_operation VARCHAR CHECK(type_of_operation IN ['create', 'modify', 'delete', 'move']),
                zip_file_number INTEGER NOT NULL,
                FOREIGN KEY (plugin_slug) REFERENCES dynamic_analysis (plugin_slug)
            );
        
        """)

con.close()