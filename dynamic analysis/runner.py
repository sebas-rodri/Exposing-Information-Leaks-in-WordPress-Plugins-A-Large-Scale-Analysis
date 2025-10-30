import requests as req

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

def get_default_value_for_type(arg_type: str):
    match arg_type:
        case "string":
            return "test"
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
            return "123"
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
            possible_routes[methods[0]].append(f"{base_url}")
            continue
        for arg, arg_details in args.items():
            for method in methods:
                type_ = arg_details.get("type", "string")
                if "enum" in arg_details:
                    for enum_value in arg_details["enum"]:
                        possible_routes[method].append(f"{base_url}?{arg}={enum_value}")
                possible_routes[method].append(f"{base_url}?{arg}={get_default_value_for_type(type_)}")
                possible_routes[method].append(f"{base_url}?{arg}={get_wrong_value_for_type(type_)}") #empty value
        
        possible_routes[method].append(f"{base_url}") #without the argument
                
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
    for method, endpoints in possible_endpoints.items():
        if method == "GET":
            for endpoint in endpoints:
                resp = req.get(endpoint)
                print(f"GET {endpoint} - Status: {resp.status_code}, Response: {resp.text}")
        elif method == "POST":
            for endpoint in endpoints:
                resp = req.post(endpoint)
                print(f"POST {endpoint} - Status: {resp.status_code}, Response: {resp.text}")
        elif method == "PUT":
            for endpoint in endpoints:
                req.put(endpoint)
        elif method == "DELETE":
            for endpoint in endpoints:
                req.delete(endpoint)
        elif method == "PATCH":
            for endpoint in endpoints:
                req.patch(endpoint)
    pass

def main():
    ajax_endpoints = find_ajax_endpoints()
    find_rest_api_endpoints()
    


if __name__ == "__main__":
    main()