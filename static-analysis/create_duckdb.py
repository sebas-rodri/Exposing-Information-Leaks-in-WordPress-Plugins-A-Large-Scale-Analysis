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
        """)

#Create Tables
con.sql("""
        CREATE TABLE IF NOT EXISTS semgrep_runs (
            run_id INTEGER DEFAULT(nextval('run_ids')) PRIMARY KEY,
            plugin_slug VARCHAR NOT NULL UNIQUE,
            plugin_version VARCHAR NOT NULL,
            plugin_download_link VARCHAR NOT NULL,
            plugin_num_dowloads INTEGER NOT NULL,
            active_installations INTEGER NOT NULL,
            duration FLOAT NOT NULL,
            error_count INTEGER NOT NULL
            );
        
        CREATE TABLE IF NOT EXISTS rules (
            rule_id VARCHAR NOT NUll PRIMARY KEY,
            severity VARCHAR NOT NULL CHECK(severity IN ['INFO', 'ERROR', 'WARNING']),
            sink VARCHAR
        );
        CREATE TABLE IF NOT EXISTS findings (
            finding_id INTEGER DEFAULT(nextval('finding_ids')) PRIMARY KEY,
            run_id INTEGER NOT NULL,
            rule_id VARCHAR NOT NULL,
            file_path VARCHAR NOT NULL,
            start_line INTEGER NOT NULL,
            end_line INTEGER NOT NULL,
            message VARCHAR,
            FOREIGN KEY (rule_id) REFERENCES rules (rule_id),
            FOREIGN KEY (run_id) REFERENCES semgrep_runs (run_id)
            );
        
        -- This is the mapping for the rules
        """)

con.close()