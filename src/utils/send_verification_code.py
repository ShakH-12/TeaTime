import requests
from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = 'https://gatewayapi.telegram.org/'
TOKEN = os.getenv("TELEGRAM_GETAWAY_TOKEN")
HEADERS = {
    'Authorization': f'Bearer {TOKEN}',
    'Content-Type': 'application/json'
}


def post_request_status(endpoint, json_body):
    url = f"{BASE_URL}{endpoint}"
    response = requests.post(url, headers=HEADERS, json=json_body)
    if response.status_code == 200:
        response_json = response.json()
        if response_json.get('ok'):
            res = response_json.get('result', {})
            return {"ok": True, "data": res}
        else:
            error_message = response_json.get('error', 'Unknown error')
            return {"ok": False, "error": f"Error: {error_message}"}
    else:
        return {"ok": False, "error": f"Failed to get request status: HTTP {response.status_code}"}

'''
SEND CODE

endpoint = "sendVerificationMessage"

json_body = {
    'phone_number': PHONE,         # Must be the one tied to request_id
    'code_length': 7,              # Ignored if you specify your own 'code'
    'ttl': 60,                     # 1 minute
    'payload': 'my_payload_here',  # Not shown to users
    'callback_url': 'https://my.webhook.here/auth'
}


CHECK STATUS
endpoint = "checkVerificationStatus"

json_body = {
    'request_id': result["request_id"], # Relevant request id
    'code': CODE,             # The code the user entered in your app
}

'''


