# Authorize.Net

apiLoginId = "9W2eg3tJw"
transactionKey = "8YKqd5pCjL6465S5"

#
# Payeezy
#
url_payeezy_sandbox = 'https://api-cert.payeezy.com/v1/transactions'

# Se introducen en el header del HTTP POST para el API. API sandbox para el proyecto.
headers = {

            'apikey': 'XDThcAW9RGkcU8fJNWu6v5GZIYQ1WEEI',
           'token': 'fdoa-a480ce8951daa73262734cf102641994c1e55e7cdf4c02b6',
           'Content-type': 'application/json',
           'Authorization': 'N2Y0ODI5MTgyMWRhOWQ5NDkyMzdmODFkNWY0OGE4NGFjYjI5YzMzNDI2MTdiYjI2YmY3NmVkOWNhYjc0NWUwZQ==',
           'nonces': '3116981424370852400',
           'timestamp': '1510690506884'
           }

# Transaction's Payload
payload = {
          "merchant_ref": "Marine parts",
          "transaction_type": "purchase",
          "method": "token",
          "amount": '0',
          "currency_code": "USD",
          "token": {
            "token_type": "FDToken",
            "token_data": {
              "type": "visa",
              "value": '',
              "cardholder_name": "xyz",
              "exp_date": "1220"
              # "special_payment": "B"
            }
          }
        }