"""Handler for errors"""


def handle_response(response):
    """Handle API response and return appropriate result or error"""
    if response.status_code == 200:
        return response.json()

    elif response.status_code == 201:
        return response.json()

    elif response.status_code == 202:
        return response.json()

    elif response.status_code == 400:
        return {
            "error": response.json().get("message"),
            "status_code": response.status_code,
        }

    elif response.status_code == 403:
        return {
            "error": response.json().get("message"),
            "status_code": response.status_code,
        }

    elif response.status_code == 404:
        return {
            "error": response.json().get("message"),
            "status_code": response.status_code,
        }

    elif response.status_code == 503:
        return {
            "error": response.json().get("message"),
            "status_code": response.status_code,
        }

    elif response.status_code == 500:
        return {
            "error": response.json().get("message"),
            "status_code": response.status_code,
        }

    elif response.status_code == 401:
        return {
            "error": response.json().get("message"),
            "status_code": response.status_code,
        }

    else:
        return {"error": f"An unknown error occurred: {response.status_code}"}
