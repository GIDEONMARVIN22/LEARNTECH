import requests
import os

# ── Pesapal Credentials ─────────────────────────────────────────────────────
CONSUMER_KEY = os.environ.get('PESAPAL_CONSUMER_KEY', 'H5SWGRob0bcyZvsiVH52jwrAdCaRsEqK')
CONSUMER_SECRET = os.environ.get('PESAPAL_CONSUMER_SECRET', 'Ji55j2AxS7+CQQxptP+g/PQUDwI=')

# Sandbox: https://cybqa.pesapal.com/pesapalv3
# Live:    https://pay.pesapal.com/v3
BASE_URL = os.environ.get('PESAPAL_BASE_URL', 'https://cybqa.pesapal.com/pesapalv3')
CALLBACK_URL = os.environ.get('PESAPAL_CALLBACK_URL', 'https://learntech.onrender.com/pesapal/callback')


def get_access_token():
    """Get OAuth token from Pesapal."""
    url = f'{BASE_URL}/api/Auth/RequestToken'
    res = requests.post(url, json={
        'consumer_key': CONSUMER_KEY,
        'consumer_secret': CONSUMER_SECRET
    }, headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, timeout=30)
    res.raise_for_status()
    return res.json()['token']


def register_ipn():
    """Register your callback URL with Pesapal (do this once)."""
    token = get_access_token()
    url = f'{BASE_URL}/api/URLSetup/RegisterIPN'
    res = requests.post(url, json={
        'url': CALLBACK_URL,
        'ipn_notification_type': 'GET'
    }, headers={
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }, timeout=30)
    res.raise_for_status()
    return res.json()['ipn_id']


def submit_order(amount, description, reference, email, phone, first_name, last_name, ipn_id):
    """Submit a payment order and get back a redirect URL."""
    token = get_access_token()
    url = f'{BASE_URL}/api/Transactions/SubmitOrderRequest'
    payload = {
        'id': reference,
        'currency': 'KES',
        'amount': amount,
        'description': description,
        'callback_url': CALLBACK_URL,
        'notification_id': ipn_id,
        'billing_address': {
            'email_address': email,
            'phone_number': phone,
            'first_name': first_name,
            'last_name': last_name,
        }
    }
    res = requests.post(url, json=payload, headers={
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }, timeout=30)
    res.raise_for_status()
    data = res.json()
    return data['redirect_url'], data['order_tracking_id']


def get_transaction_status(order_tracking_id):
    """Check if a payment was completed."""
    token = get_access_token()
    url = f'{BASE_URL}/api/Transactions/GetTransactionStatus?orderTrackingId={order_tracking_id}'
    res = requests.get(url, headers={
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json'
    }, timeout=30)
    res.raise_for_status()
    return res.json()
