import json

with open("runner/function_hooking_fresh_instance.json", "r") as f:
    jsonl = list(f)
    

paths_to_filter_out = set()

for json_line in jsonl:
    j = json.loads(json_line)
    params = j.get("params")[0]
    paths_to_filter_out.add(params)

with open("runner/baseline_paths.py", "w") as f:
    f.write("BASELINE_PATHS = {\n")
    for p in sorted(paths_to_filter_out):
        f.write(f'    "{p}",\n')
    f.write("}\n")
