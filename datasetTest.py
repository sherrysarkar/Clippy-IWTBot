import requests
import json
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from datetime import date
import pandas as pd

auth_data = {
    "grant_type"    : "client_credentials",
    "client_id"     : "c5af737ef38e4e3ca23adce3cf9bb070",
    "client_secret" : "72e10987eb4587b50863765b4c7c81ba93d23962cff4ca0b93e27d64da592e53",
    "scope"         : "read_product_data read_financial_data read_content"
}

# create session instance
session = requests.Session()

auth_request = session.post("https://idfs.gs.com/as/token.oauth2", data = auth_data)
# print('Response {}'.format(auth_request.text))

access_token_dict = json.loads(auth_request.text)
access_token = access_token_dict["access_token"]

# print('Access Token {}'.format(access_token))

# update session headers with access token
session.headers.update({"Authorization":"Bearer "+ access_token})

coverage_request_url = 'https://api.marquee.gs.com/v1/data/USCANFPP_MINI/coverage?limit=500'
request_url = "https://api.marquee.gs.com/v1/data/USCANFPP_MINI/query"
reference_request_url = 'https://api.marquee.gs.com/v1/assets/data/query'



coverage = session.get(url=coverage_request_url)
coverage_data = json.loads(coverage.text)

reference_query = {
    'where': {
        'gsid': [datapoint['gsid'] for datapoint in coverage_data['results']]
    },
    'fields': ['gsid', 'ticker', 'name'],
    'limit': 500
}

reference = session.post(url=reference_request_url, json=reference_query)
reference_data = json.loads(reference.text)
companies_set = {(result['ticker'], result['name'], result['gsid']) for result in reference_data['results']}
print('{} companies:'.format(len(companies_set)))
print('\n'.join([str(asdf) for asdf in list(companies_set)]))


start_date = date(2010, 1, 15)

companies = ['AAPL', 'FB']
gsids = ['227284']
request_query = {
    "where": {
        "gsid": gsids
    },
    "startDate": start_date.isoformat(),
    # "endDate":'2018-01-15'
}



request = session.post(url=request_url, json=request_query)
results = json.loads(request.text)
print(results)
data = results['data']

print(len(data))

###### Graphing #######

# 'growthScore': 0.234, 'multipleScore': 0.076, 'gsid': '901237', 'financialReturnsScore': 0.71,'c': 0.624

stats = ['growthScore', 'multipleScore', 'financialReturnsScore', 'integratedScore']


company_stats = {company: {stat: [] for stat in stats} for company in companies}

X = {company: 0 for company in companies}
days = {company: [] for company in companies}

for j, entry in enumerate(data):
    comp = entry['ticker']

    for stat in stats:
        if stat in entry.keys():
            company_stats[comp][stat].append(entry[stat])
        else:
            print('key error: {}, {}, {}'.format(comp, X[comp], stat))
            company_stats[comp][stat].append(company_stats[comp][stat][-1])

    num_days = (date(*(int(a) for a in entry['date'].split('-'))) - start_date).days
    days[comp].append(num_days)
    X[comp] += 1



print({comp: len(company_stats[comp]['growthScore']) for comp in companies})

fig, ax = plt.subplots()
plt.plot(days['AAPL'], company_stats['AAPL']['financialReturnsScore'], color="green")
plt.plot(days['FB'], company_stats['FB']['financialReturnsScore'], color="blue")

#print(np.corrcoef(finReturnScores['AAPL'][:75], finReturnScores['FB'][:75])[0, 1])

#plt.plot(X, finReturnScore, color="red")
#plt.plot(X, intergratedScore, color="black")


ax.set(xlabel='time (days)', ylabel='Scores',
       title='Different Scores')
ax.grid()

plt.show()
