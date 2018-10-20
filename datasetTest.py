import requests
import json

auth_data = {
    "grant_type"    : "client_credentials",
    "client_id"     : "c5af737ef38e4e3ca23adce3cf9bb070",
    "client_secret" : "72e10987eb4587b50863765b4c7c81ba93d23962cff4ca0b93e27d64da592e53",
    "scope"         : "read_product_data read_financial_data read_content"
}

# create session instance
session = requests.Session()

auth_request = session.post("https://idfs.gs.com/as/token.oauth2", data = auth_data)
print('Response {}'.format(auth_request.text))

access_token_dict = json.loads(auth_request.text)
access_token = access_token_dict["access_token"]

print('Access Token {}'.format(access_token))

# update session headers with access token
session.headers.update({"Authorization":"Bearer "+ access_token})

coverage_request_url = 'https://api.marquee.gs.com/v1/data/USCANFPP_MINI/coverage?limit=100'
request_url = "https://api.marquee.gs.com/v1/data/USCANFPP_MINI/query"
reference_request_url = 'https://api.marquee.gs.com/v1/assets/data/query'


request_query = {
                    "where": {
                        "gsid": ["901237","11308","177256"]
                    },
                    "startDate": "2017-01-15",
                    "endDate":"2018-01-15"
               }

reference_query = {
    "where": {
        "ticker": [ "GOOG", "AAPL", "FB", "MSFT" ]
    },
    "fields": [ "gsid", "ticker", 'name'],
    "limit": 1000
}



coverage = session.get(url=coverage_request_url)
coverage_data = json.loads(coverage.text)
print(coverage_data)

reference = session.post(url=reference_request_url, json=reference_query)
reference_data = json.loads(reference.text)
print(reference_data)

# request = session.post(url=request_url, json=request_query)
# results = json.loads(request.text)
# print(results)
