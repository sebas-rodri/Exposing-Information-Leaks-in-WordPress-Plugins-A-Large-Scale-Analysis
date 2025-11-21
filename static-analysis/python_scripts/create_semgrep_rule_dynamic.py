import json
import os
import re

slug = os.environ['slug']
data = json.load(open(f"./results/{slug}/ajax.json"))
closure_output = f"./results/{slug}/ajax_closure.json"
ajax_function_output = f"./results/{slug}/ajax_function.json"
semgrep_rules_path_base =  f"./results/{slug}/semgrep-rules-ajax/"

os.makedirs(semgrep_rules_path_base, exist_ok=True)

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
result_closure_json = []
    
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
    result_closure_json.append({"priv": priv, "action": ajax_route, "args": args})

#os.makedirs(os.path.dirname(closure_output), exist_ok=True)
with open(closure_output, 'w') as f:
    json.dump(result_closure_json, f, indent=2)



#Make Semgrep Rule depending on $NAME
ajax_route_array = []
for hook, function_name in ajax_function_names.items():
    hook = hook.strip("'\".\'")
    yaml = f"""
rules:
  - id: {hook}
    languages:
      - php
    severity: ERROR
    message: |
      Semgrep found a match
    patterns:
      - patterns:
          - pattern: function $FUNC (...){{...}}
          - patterns:
              - pattern: $METHOD["$ARG"]
              - metavariable-pattern:
                  metavariable: $METHOD
                  pattern-regex: \$_(REQUEST|POST|FILES|GET)
          - metavariable-regex:
              metavariable: $FUNC
              regex: {function_name}
    """
    open(semgrep_rules_path_base+f"{hook}.yml", "w").write(yaml)
    #Save ajax_routes
    if hook.startswith("wp_ajax_nopriv_"):
        priv = False
        action = hook.replace("wp_ajax_nopriv_", "", 1)
    elif hook.startswith("wp_ajax_"):
        priv = True
        action = hook.replace("wp_ajax_", "", 1)
    ajax_route_array.append({"action": action, "priv": priv})

with open(ajax_function_output, 'w') as f:
    json.dump(ajax_route_array, f, indent=2)


print("CLOSURE:"+ str(result_closure_json) + "\n\n\n")
print(ajax_function_names)