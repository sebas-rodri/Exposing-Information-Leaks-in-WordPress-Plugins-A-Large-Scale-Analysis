import requests as req
import time
import json
import os
import datetime
import duckdb
import sys
import string
from parse_results_to_db import parse_jsonl, save_analysis_metrics, save_function_hooking_results

"""
REST endpoints called
REST ENDPOINTS with 200

RESULTS -> Alles Abspeichern als zip aber mit sinvollem Name
Parsen von JSON am ende und abspeichern in duckdb


AJAX ENDPOINTS called
"""
DB_NAME = "results.db"
PLUGIN_SLUG = os.environ.get("PLUGIN_SLUG")
NUM_UNIQUE_REST_ENDPOINTS = 0
NUM_REST_ENDPOINTS_CALLED = 0
NUM_REST_ENDPOINTS_HTTP_OK = 0
TIMEOUT_REST_REQ = 2 #This should be more then enough


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
    BASE = "http://localhost:8080"
    AJAX = f"{BASE}/wp-admin/admin-ajax.php?"
    LOGIN = f"{BASE}/wp-login.php"
    admin_name = "admin"
    admin_pwd =  "secret"
    user_name = "author@author.de"
    user_pwd = "author"
    
    def __init__(self, timeout: int = 120):
        self.timeout = timeout
        self.con = duckdb.connect(DB_NAME)
        self.num_ajax_endpoints = 0
        self.num_ajax_endpoints_called = 0
        self.num_ajax_endpoints_http_ok = 0
        self.endpoints = None
        self.user_session = self.login(AjaxRunner.user_name, AjaxRunner.user_pwd)
        self.admin_session = self.login(AjaxRunner.admin_name, AjaxRunner.admin_pwd)
        self.get_endpoints()
    
    def login(self, name, pwd):
        session = req.Session()
        headers1 = { 'Cookie':'wordpress_test_cookie=WP Cookie check' }
        datas={ 
        'log':name, 'pwd':pwd, 'wp-submit':'Log In', 
        'redirect_to': AjaxRunner.BASE, 'testcookie':'1'  
        }
        res = session.post(AjaxRunner.LOGIN, headers=headers1, data=datas)
        return session
        
    
    def get_endpoints(self):
        self.endpoints = self.con.execute("""
        SELECT * FROM ajax_routes WHERE plugin_slug = ?
        """, [PLUGIN_SLUG]).fetchall()
        

        self.num_ajax_endpoints = len(self.endpoints)
    
    def get_arguments_endpoint(self, route_id):
        arguments = self.con.execute("""
                                     SELECT method, arg_name
                                     FROM ajax_route_arguments
                                     WHERE route_id = ?
                                     """, [route_id]).fetchall()
        return arguments
    

    def create_data_from_arg(self, arguments, unexpected=False):
        '''
        5 Test Cases: INT MAX/MIN, all strings, BOOLEAN, argument php
        '''
        method_data = []
        all_args_payload = {}
        for arg in arguments:
            method = arg[0]
            arg_name = arg[1]
            method_data.append((method, {arg_name: sys.maxsize}))
            method_data.append((method, {arg_name: -sys.maxsize}))
            method_data.append((method, {arg_name: string.printable}))
            method_data.append((method, {arg_name: True}))
            method_data.append((method, {arg_name: False}))
            method_data.append((method, {arg_name: 0.0123456789}))
            method_data.append((method, {f'{arg_name}[]': sys.maxsize}))
            method_data.append((method, {f'{arg_name}[]': -sys.maxsize}))
            method_data.append((method, {f'{arg_name}[]': string.printable}))
            method_data.append((method, {f'{arg_name}[]': True}))
            method_data.append((method, {f'{arg_name}[]': False}))
            method_data.append((method, {f'{arg_name}[]': 0.0123456789}))
            all_args_payload[arg_name] = string.printable
        
        method_data.append(("POST", all_args_payload))
        method_data.append(("GET", all_args_payload))
        
        return method_data
        
        

    def call_endpoints(self):
       for endpoint in self.endpoints:
            arguments = self.get_arguments_endpoint(route_id=endpoint[0])
            action = endpoint[2]
            priv = endpoint[3]
            try:
                if len(arguments) > 0:
                    for method, data in self.create_data_from_arg(arguments):
                    
                        write_data = {"interface": "AJAX", "method": method, "url": AjaxRunner.AJAX, "data": data}
                        write_test(write_data)
                        wait_if_change_detected()
                        if method == "POST":
                            response = self.user_session.post(AjaxRunner.AJAX, data={"action": action, **data}, timeout=1)
                            response_admin = self.admin_session.post(AjaxRunner.AJAX, data={"action": action, **data}, timeout=1)
                        elif method == "FILES":
                            response = self.user_session.post(AjaxRunner.AJAX, files={"action": action, **data}, timeout=1)
                            response_admin = self.admin_session.post(AjaxRunner.AJAX, files={"action": action, **data}, timeout=1)
                        else:
                            response = self.user_session.get(AjaxRunner.AJAX, params={"action": action, **data}, timeout=1)
                            response_admin = self.user_session.get(AjaxRunner.AJAX, params={"action": action, **data}, timeout=1)
                        log.status(response, f"AJAX Action: {action} with data {data}")
                        log.status(response_admin, f"AJAX Action: {action} with data {data}")
                    for method, data in self.create_data_from_arg(arguments, unexpected=True):
                        
                        write_data = {"interface": "AJAX", "method": method, "url": AjaxRunner.AJAX, "data": data}
                        write_test(write_data)
                        wait_if_change_detected()
                        if method == "POST":
                            response = self.user_session.post(AjaxRunner.AJAX, data={"action": action, **data}, timeout=1)
                            response_admin = self.admin_session.post(AjaxRunner.AJAX, data={"action": action, **data}, timeout=1)
                        elif method == "FILES":
                            response = self.user_session.post(AjaxRunner.AJAX, files={"action": action, **data}, timeout=1)
                            response_admin = self.admin_session.post(AjaxRunner.AJAX, files={"action": action, **data}, timeout=1)
                        else:
                            response = self.user_session.get(AjaxRunner.AJAX, params={"action": action, **data}, timeout=1)
                            response_admin = self.admin_session.get(AjaxRunner.AJAX, params={"action": action, **data}, timeout=1)
                        log.status(response, f"AJAX Action: {action} with unexpected data {data}")
                        log.status(response_admin, f"AJAX Action: {action} with unexpected data {data}")
                    self.num_ajax_endpoints_called += 1
                else:
                    #No arguments in AJAX action
                    write_data = {"interface": "AJAX", "method": "POST", "url": AjaxRunner.AJAX, "data": {"action": action}}
                    write_test(write_data)
                    wait_if_change_detected()
                    response = self.user_session.post(AjaxRunner.AJAX, data={"action": action}, timeout=1)
                    response_admin = self.admin_session.post(AjaxRunner.AJAX, data={"action": action}, timeout=1)
                    log.status(response, f"AJAX Action: {action} without data")
                    log.status(response_admin, f"AJAX Action: {action} without data")
                    self.num_ajax_endpoints_called += 1
            except req.exceptions.RequestException as e:
                    log.red(f"Error calling AJAX Action: {action} without data: {e}")
                    
           
    
    def run(self):
        self.call_endpoints()
        self.con.close()
        
    


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

REST = "/wp-json/"
STANDARD_NAMESPACES = [
    "wp/v2", "oembed/1.0", "wp-site-health/v1", "wp-block-editor/v1"]
BASE = "http://localhost:8080"

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
    #More variation number range, true false, empty array
    match arg_type:
        case "string":
            return get_string_for_format(format) if format else string.printable
        case "null":
            return None
        case "boolean":
            return True
        case "integer":
            return sys.maxsize
        case "number":
            return 1.23456789
        case "array":
            return [string.printable, 123, True, None]
        case "object":
            return {string.printable: string.printable}
    return string.printable

def get_wrong_value_for_type(arg_type: str):
    match arg_type:
        case "string":
            return sys.maxsize
        case "null":
            return sys.maxsize
        case "boolean":
            return sys.maxsize
        case "integer":
            return string.printable
        case "number":
            return string.printable
        case "array":
            return string.printable
        case "object":
            return string.printable
    return string.printable

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
                    
    NUM_UNIQUE_REST_ENDPOINTS = len(possible_routes.values())         
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

def wait_if_change_detected():
    while True:
        if os.path.exists(".change"):
            print("Change detected, sleep 0.05")
            time.sleep(0.05)
        else:
            break

def call_rest_api_endpoints(possible_endpoints):
    #create filewrite on volume, so watcher can know which endpoints were called
    for method, endpoint_configs in possible_endpoints.items():
        for config in endpoint_configs:
            print(f"Calling {method} {config}")
            url = config["url"]
            
            try:
                write_data = {"interface": "REST", "method": method, "url": config.get("url"), "data": config.get("data", {})}
                write_test(write_data)
                wait_if_change_detected()
                NUM_REST_ENDPOINTS_CALLED += 1
                if method == "GET":
                    response = req.get(url, timeout=TIMEOUT_REST_REQ)
                    
                elif method == "POST":
                    data = config.get("data", {})
                    # Try both JSON and form data
                    response = req.post(url, json=data, timeout=TIMEOUT_REST_REQ)
                    log.status(response, f"{url} (JSON: {data})")
                    if data:
                        response = req.post(url, data=data, timeout=TIMEOUT_REST_REQ)
                        log.status(response, f"{url} (Form: {data})")
                    
                elif method == "PUT":
                    data = config.get("data", {})
                    response = req.put(url, json=data, timeout=TIMEOUT_REST_REQ)
                    
                elif method == "DELETE":
                    response = req.delete(url, timeout=TIMEOUT_REST_REQ)
                    
                elif method == "PATCH":
                    data = config.get("data", {})
                    response = req.patch(url, json=data, timeout=TIMEOUT_REST_REQ)
                if response.ok:
                    NUM_REST_ENDPOINTS_HTTP_OK += 1
                log.status(response, url) 
            except req.exceptions.RequestException as e:
                log.red(f"Error calling {method} {url}: {e}")
        
    

def main():
    time.sleep(2) #Wait for watcher to be ready
    start = time.time()
    ajax = AjaxRunner()
    ajax.run()
    find_rest_api_endpoints()
    end = time.time()
    total_time_spent = end - start
    ## Call Save methods
    parse_jsonl(PLUGIN_SLUG)
    save_analysis_metrics(PLUGIN_SLUG,
                          num_unique_rest_endpoints=NUM_UNIQUE_REST_ENDPOINTS, 
                            num_rest_endpoints_called=NUM_REST_ENDPOINTS_CALLED,
                            num_rest_endpoints_http_ok=NUM_REST_ENDPOINTS_HTTP_OK, 
                            num_ajax_endpoints=ajax.num_ajax_endpoints,
                            num_ajax_endpoints_called=ajax.num_ajax_endpoints_called,
                            num_ajax_endpoints_http_ok=ajax.num_ajax_endpoints_http_ok,
                            time_spend=total_time_spent)
    save_function_hooking_results(slug=PLUGIN_SLUG)
    print("Dynamic Analysis Finished")


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
    #TODO: Change when production
    while True:
        time.sleep(10)
   