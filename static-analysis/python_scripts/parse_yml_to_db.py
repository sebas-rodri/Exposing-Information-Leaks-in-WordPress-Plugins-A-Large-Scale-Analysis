import sys
import os
import yaml
import duckdb
from yaml.loader import SafeLoader

"""
This parses the yml rules into the duckdb database,
to have a mapping of rule_id
"""

if len(sys.argv) != 3:
    print("Usage: python parse_yml_to_db.py <path_to_yml_file> <path_to_duckdb>")
    sys.exit(1)

yml_file = sys.argv[1]
if not os.path.exists(yml_file):
    print(f"Error: The file {yml_file} does not exist.")
    sys.exit(1)

with open(yml_file, 'r') as f:
    rules = list(yaml.load_all(f, Loader=SafeLoader))
    rules = rules[0]["rules"]
    

con = duckdb.connect(sys.argv[2])

for rule in rules:
    rule_id = rule.get("id")
    severity = rule.get("severity")
    sink = rule_id.split("_")
    if len(sink) != 2:
        sink = None
    else:
        sink = sink[0]
    
    con.sql("""
            INSERT INTO rules (rule_id, severity, sink) VALUES (?, ?, ?);
            """,params= (rule_id, severity, sink))


#test if inserted correctly
#rules = con.sql("SELECT * FROM rules LIMIT 10").fetchall()
#print(rules)


con.close()