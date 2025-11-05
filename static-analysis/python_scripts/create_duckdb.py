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
        CREATE TABLE IF NOT EXISTS plugins (
            name VARCHAR NOT NULL,
            slug VARCHAR NOT NULL UNIQUE,
            version VARCHAR NOT NULL,
            download_link VARCHAR NOT NULL,
            num_downloads INTEGER NOT NULL,
            active_installations INTEGER NOT NULL,
            PRIMARY KEY (slug)
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
        
        -- This is the mapping for the rules
        """)

con.close()