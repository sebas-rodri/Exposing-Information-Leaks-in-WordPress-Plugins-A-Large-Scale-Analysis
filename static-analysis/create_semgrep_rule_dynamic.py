import json
import os
import re

data = json.load(open("/Users/sebastianrodriguez/Desktop/Informatik Studium/Semester6/Bachelorarbeit/Exposing-Information-Leaks-in-WordPress-Plugins-A-Large-Scale-Analysis/static-analysis/ajax.json"))
slug = os.environ['slug']
print(slug)

pattern = re.compile(
    r'\$_(?P<method>REQUEST|POST|FILES|GET)\s*'
    r'\[\s*'
    r'(?P<quote>[\'"])'
    r'(?P<arg>[^\'"]+)'
    r'(?P=quote)\s*\]'
)

ajax_function_names = {}
ajax_closures = {}

for result in data["results"]:
    extra = result.get("extra", {})
    metavars = extra.get("metavars", {})
    #print(metavars)
    if "$HOOK" in metavars and "$NAME" in metavars:
        name = metavars["$NAME"]["abstract_content"]
        hook = metavars["$HOOK"]["abstract_content"]
        ajax_function_names[hook] = name
    if "$HOOK" in metavars and "$CLOSURE" in metavars:
        hook = metavars["$HOOK"]["abstract_content"]
        closure = metavars["$CLOSURE"]["abstract_content"]
        ajax_closures[hook] = closure
    

for wp_ajax, function_name in ajax_function_names.items():
    print(wp_ajax, function_name)
    

#CLOSURE RESULTS
result_closure_json = {slug: {}}
    
for wp_ajax, closure in ajax_closures.items():
    priv = True
    wp_ajax = wp_ajax.strip("'\"")
    #Case it wasnt really a closure
    if not closure.startswith("function"):
        continue
    ajax_route = wp_ajax.replace("wp_ajax_","")
    if ajax_route.startswith("nopriv_"):
        ajax_route = ajax_route.replace("nopriv_", "")
        priv = False
    args = []
    for m in pattern.finditer(closure):
        method = m.group('method')
        arg = m.group('arg')
        print(method, arg)
        args.append([method, arg])
    result_closure_json[slug][ajax_route] = {"priv": priv, "action": ajax_route, "args": args}

closure_output = f"./results/{slug}/ajax_closure.json"
#os.makedirs(os.path.dirname(closure_output), exist_ok=True)
with open(closure_output, 'w') as f:
    json.dump(result_closure_json, f, indent=2)
print(result_closure_json)
print(ajax_function_names)