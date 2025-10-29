'''
This part is responsible for AJAX, finding actions, and calling them
'''
BASE = "http://localhost:8080"
AJAX = "/wp-admin/admin-ajax.php"
REST = "/wp-json"

def find_ajax_endpoints() -> list:
    return []

def call_ajax_endpoint(endpoints: list):
    for endpoint in endpoints:
        continue

def find_rest_api_endpoints() -> list:
    return []

def call_rest_api_endpoint():
    pass

def main():
    print("Dynamic analysis runner")
    ajax_endpoints = find_ajax_endpoints()
    


if __name__ == "__main__":
    main()