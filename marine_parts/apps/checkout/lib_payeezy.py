import requests
import constants
# import required libs to generate HMAC
import os, hashlib, hmac, time, base64, json


def setup_params_request(price, card_type, token, cardholder_name, exp_date):
    payload = {
        "merchant_ref": "Marine parts",
        "transaction_type": "purchase",
        "method": "token",
        "amount": price.replace('.',''),
        "currency_code": "USD",
        "token": {
            "token_type": "FDToken",
            "token_data": {
                "type": card_type,
                "value": token,
                "cardholder_name": cardholder_name,
                "exp_date": exp_date
            }
        }
    }

    nonces = get_nonces()
    timestamp = get_timestamp()
    hmac = gen_hmac(timestamp, nonces
                    , constants.apiKey, constants.apiSecret, constants.token_live, json.dumps(payload))
    # Use 'token_live' when it is deployed
    # hmac = gen_hmac(timestamp, nonces
    #                 , constants.apiKey, constants.apiSecret, constants.token, json.dumps(payload))

    headers = {
        'apikey': constants.apiKey,
        # Use 'token_live' when it is deployed
        #'token': constants.token,
        'token': constants.token_live,
        'Content-type': 'application/json',
        'Authorization': hmac,
        'nonce': nonces,
        'timestamp': timestamp
    }
    return (headers, payload)

def execPaymentPayeezySandbox(order_number, payload, headers):
    return execPaymentPayeezy(constants.url_payeezy_sandbox, order_number, payload, headers)

def execPaymentPayeezyLive(order_number, payload, headers):
    return execPaymentPayeezy(constants.url_payeezy_live, order_number, payload, headers)

def execPaymentPayeezy(url, order_number, headers, payload):
    # Charge the token requested
    response = requests.post(url, json=payload, headers=headers)
    response_json = response.json()
    # Check errors
    if response.status_code >= 400:
        # print("Transaction status: " + response_json['transaction_status'])
        # for x in response_json['Error']['messages']:
        #     print(x['code'] + " " + x['description'])
        return (False, None)
    else:

        # Notify payment event if there is success
        reference = "Transaction ID: %s\nBank response code: %s\n, Bank message: %s\n" \
                    % (
                        response_json['transaction_id'], response_json['bank_resp_code'], response_json['bank_message'])
        return (True, reference)

def get_nonces():
    # Crypographically strong random number
    return str(int(os.urandom(16).encode('hex'), 16))

def get_timestamp():
    # Epoch timestamp in milli seconds
    return str(int(round(time.time() * 1000)))

def gen_hmac(timestamp, nonce, apikey, apiSecret, token, payload ):
    # All parameters must be string
    data = apikey + nonce + timestamp + token + payload
    # Make sure the HMAC hash is in hex
    hmacc = hmac.new(apiSecret, msg=data, digestmod=hashlib.sha256).hexdigest()

    # Authorization : base64 of hmac hash
    autho = base64.b64encode(hmacc)
    return autho

