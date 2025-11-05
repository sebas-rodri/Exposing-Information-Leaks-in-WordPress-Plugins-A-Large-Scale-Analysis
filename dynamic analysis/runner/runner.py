import requests as req
import time
import json
import os
import datetime

"""
REST endpoints called
REST ENDPOINTS with 200

RESULTS -> Alles Abspeichern als zip aber mit sinvollem Name
Parsen von JSON am ende und abspeichern in duckdb


AJAX ENDPOINTS called
"""

class log:
    def status(response: req.Response, text):
        if response.status_code == 200:
            log.green(f"{response.request.method} {text} - Status: {response.status_code}, Response: {response.text}")
        elif response.status_code >= 500:
            log.red(f"{response.request.method} {text} - Status: {response.status_code}, Response: {response.text}")
        else: 
            log.blue(f"{response.request.method} {text} - Status: {response.status_code}, Response: {response.text}")
    
    def green(text):
        print('\033[92m' + text + '\033[0m')
    
    def blue(text):
        print('\033[94m' + text + '\033[0m')
    
    def red(text):
        print('\033[91m' + text + '\033[0m')
    
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'   
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class RestAPIRunner:
    def __init__(self, timeout: int = 120):
        self.timeout = timeout

class AjaxRunner:
    def __init__(self, timeout: int = 120):
        self.timeout = timeout


def write_test(data):
    '''Passed data should follow format:
    {interface: , method: , url: , data: }'''
    if not os.path.exists("shared"):
        exit("/shared/ Volume not mounted")
    if not os.path.exists(FILE_PATH):
        open(FILE_PATH, "w").close()
        
    with open(FILE_PATH, "+w") as f:
        f.write(json.dumps(data))
    

FILE_PATH = "shared/current_test.txt"
TIMEOUT = 2 #Low, Due to high number of requests
        

'''
This part is responsible for AJAX, finding actions, and calling them
'''
BASE = "http://localhost:8080"
AJAX = "/wp-admin/admin-ajax.php"
REST = "/wp-json/"
STANDARD_NAMESPACES = [
    "wp/v2", "oembed/1.0", "wp-site-health/v1", "wp-block-editor/v1"]

def find_ajax_endpoints() -> list:
    return []

def call_ajax_endpoint(endpoints: list):
    for endpoint in endpoints:
        continue

def get_relevant_rest_namespaces() -> list:
    wp_json = req.get(BASE + REST).json()
    namespaces = wp_json.get("namespaces", [])
    namespaces = [ns for ns in namespaces if ns not in STANDARD_NAMESPACES]
    return namespaces

def get_routes(namespaces: list) -> dict:
    routes = {}
    for ns in namespaces:
        ns_routes = req.get(BASE + REST + ns).json().get("routes", {})
        routes[ns] = ns_routes
    return routes

#regex routes
#batch also excluded


def get_string_for_format(format: str):
    '''returns a default string for a given format, only support
    following https://developer.wordpress.org/rest-api/extending-the-rest-api/schema/#format'''
    match format:
        case "date-time":
            return datetime.datetime.now().isoformat()
        case "uri":
            return "http://example.com"
        case "email":
            return "test@test.com"
        case "ip":
            return "127.0.0.1"
        case "uuid":
            return "123e4567-e89b-12d3-a456-426614174000"
        case "hex-color":
            return "#ffffff"
    return "test"

def get_default_value_for_type(arg_type: str, format: str = None):
    match arg_type:
        case "string":
            return get_string_for_format(format) if format else "test"
        case "null":
            return None
        case "boolean":
            return True
        case "integer":
            return 1
        case "number":
            return 1.0
        case "array":
            return ["test"]
        case "object":
            return {"key": "value"}
    return "test"

def get_wrong_value_for_type(arg_type: str):
    match arg_type:
        case "string":
            return 123
        case "null":
            return "not_null"
        case "boolean":
            return "not_boolean"
        case "integer":
            return "not_integer"
        case "number":
            return "not_number"
        case "array":
            return "not_array"
        case "object":
            return "not_object"
    return ""

def create_possible_routes(base_url: str, details: dict) -> dict:
    endpoints = details.get("endpoints", [])
    possible_routes = {"GET": [], "POST": [], "PUT": [], "DELETE": [], "PATCH": []}
    for endpoint_details in endpoints:
        args = endpoint_details.get("args", {})
        methods = endpoint_details.get("methods", [])
        if args == []:
            possible_routes[methods[0]].append({"url": base_url})
            continue
        for method in methods:
            if method == "GET":
                all_args_route1 = base_url + "?"
                all_args_route2 = base_url + "?"
                for arg, arg_details in args.items():
                    arg_type = arg_details.get("type", "string")
                    arg_format = arg_details.get("format", None)
                    if "enum" in arg_details:
                        for enum_value in arg_details["enum"]:
                            possible_routes[method].append({
                                "url": f"{base_url}?{arg}={enum_value}"

                            })
                    valid_val = get_default_value_for_type(arg_type, arg_format)
                    invalid_val = get_wrong_value_for_type(arg_type)
                    
                    possible_routes[method].append({
                        "url": f"{base_url}?{arg}={valid_val}"
                    })
                    possible_routes[method].append({
                        "url": f"{base_url}?{arg}={invalid_val}"
                    })
                    
                    all_args_route1 += f"{arg}={valid_val}&"
                    all_args_route2 += f"{arg}={invalid_val}&"
                    
                possible_routes[method].append({"url": all_args_route1.rstrip("&")}) #delete last &
                possible_routes[method].append({"url": all_args_route2.rstrip("&")})
                possible_routes[method].append({"url": base_url})
            else: #POST/PATCH/PUT/DELETE
                for arg, arg_details in args.items():
                    arg_type = arg_details.get("type", "string")
                    arg_format = arg_details.get("format")
                    
                    if "enum" in arg_details:
                        for enum_value in arg_details["enum"]:
                            possible_routes[method].append({
                                "url": base_url,
                                "data": {arg: enum_value}
                            })

                    valid_val = get_default_value_for_type(arg_type, arg_format)
                    invalid_val = get_wrong_value_for_type(arg_type)
                    
                    possible_routes[method].append({
                        "url": base_url,
                        "data": {arg: valid_val}
                    })
                    possible_routes[method].append({
                        "url": base_url,
                        "data": {arg: invalid_val}
                    })
                
                all_args_valid = {}
                all_args_invalid = {}
                for arg, arg_details in args.items():
                    arg_type = arg_details.get("type", "string")
                    arg_format = arg_details.get("format")
                    all_args_valid[arg] = get_default_value_for_type(arg_type, arg_format)
                    all_args_invalid[arg] = get_wrong_value_for_type(arg_type)
                
                if all_args_valid:
                    possible_routes[method].append({
                        "url": base_url,
                        "data": all_args_valid
                    })
                    possible_routes[method].append({"url": base_url, 
                        "data": all_args_invalid
                    })
                
                #No data
                possible_routes[method].append({"url": base_url, "data": {}})
                    
                
    return possible_routes

def test_endpoints(routes: dict):
    for ns, ns_routes in routes.items():
        for route, details in ns_routes.items():
            base_url = BASE + REST + route.lstrip("/")
            possible_routes = create_possible_routes(base_url, details)
            call_rest_api_endpoints(possible_routes)
                

def find_rest_api_endpoints() -> list:
    namespaces = get_relevant_rest_namespaces()
    routes = get_routes(namespaces)
    test_endpoints(routes)
    return []

def call_rest_api_endpoints(possible_endpoints):
    #create filewrite on volume, so watcher can know which endpoints were called
    for method, endpoint_configs in possible_endpoints.items():
        for config in endpoint_configs:
            print(f"Calling {method} {config}")
            url = config["url"]
            
            try:
                write_data = {"interface": "REST", "method": method, "url": config.get("url"), "data": config.get("data", {})}
                write_test(write_data)
                if method == "GET":
                    response = req.get(url, timeout=30)
                    
                elif method == "POST":
                    data = config.get("data", {})
                    # Try both JSON and form data
                    response = req.post(url, json=data, timeout=30)
                    log.status(response, f"{url} (JSON: {data})")
                    if data:
                        response = req.post(url, data=data, timeout=30)
                        log.status(response, f"{url} (Form: {data})")
                    
                elif method == "PUT":
                    data = config.get("data", {})
                    response = req.put(url, json=data, timeout=30)
                    
                elif method == "DELETE":
                    response = req.delete(url, timeout=30)
                    
                elif method == "PATCH":
                    data = config.get("data", {})
                    response = req.patch(url, json=data, timeout=30)
                log.status(response, url) 
            except req.exceptions.RequestException as e:
                log.red(f"Error calling {method} {url}: {e}")
        
    

def main():
    time.sleep(2) #Wait for watcher to be ready
    ajax_endpoints = find_ajax_endpoints()
    find_rest_api_endpoints()
    while True:
        time.sleep(60)

def connection_test():
    while True:
        try:
            response = req.get(BASE)
            if response.status_code == 200:
                break
            else:
                print(f"Waiting for WordPress to be ready. Status code: {response.status_code}")
        except req.exceptions.ConnectionError:
            print("Connection error.")
        time.sleep(5)


if __name__ == "__main__":
    print("Start Runner")
    connection_test()
    main()