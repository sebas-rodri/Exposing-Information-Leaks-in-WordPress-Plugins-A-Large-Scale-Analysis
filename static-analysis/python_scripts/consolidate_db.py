import duckdb
import sys

'''
Use this to merge databases after static analysis if used on parallel
'''

if len(sys.argv) < 3:
    print(f"Usage: python consolidate_db.py dbname1 dbname2 ...")
    sys.exit(1)

con = duckdb.connect(sys.argv[1])

print(sys.argv)

#Create Attachments
for i in range(len(sys.argv)):
    if i < 2:
        continue
    
    con.sql(f"""
            ATTACH '{sys.argv[i]}' as db{i}
            """)
    #Calculate offsets for semgrep_runs
    offset_semgrep_runs = con.sql(f"""
            SELECT MAX(run_id) FROM semgrep_runs;
            """).fetchone()[0]
    #Offset findings_semgrep
    offset_findings_semgrep = con.sql(f"""
            SELECT MAX(finding_id)FROM findings_semgrep;
            """).fetchone()[0]
    
    #Offset ajax_routes
    offset_ajax_routes = con.sql(f"""
             SELECT MAX(route_id) FROM ajax_routes;
            """).fetchone()[0]
    #Update
    con.sql(f"""
            BEGIN TRANSACTION;
            UPDATE db{i}.semgrep_runs
            SET run_id = run_id + {offset_semgrep_runs};
            UPDATE db{i}.findings_semgrep
            SET run_id = run_id + {offset_semgrep_runs};
            COMMIT;
            """)
    
    print(offset_semgrep_runs, offset_findings_semgrep, offset_ajax_routes)
    #Also add to to ajax_route_arguments
    
    #Insert
    con.sql(f"""
            Insert INTO plugins
            SELECT * FROM db{i}.plugins;
            """)
    con.sql(f"""
            Insert INTO semgrep_runs
            SELECT * FROM db{i}.semgrep_runs;
            """)

con.close()
#Merge 