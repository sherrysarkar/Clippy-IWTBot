import requests
import json
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from datetime import date

START_DATE = date(2015, 1, 15)


def request_data():
    auth_data = {
        "grant_type": "client_credentials",
        "client_id": "c5af737ef38e4e3ca23adce3cf9bb070",
        "client_secret": "72e10987eb4587b50863765b4c7c81ba93d23962cff4ca0b93e27d64da592e53",
        "scope": "read_product_data read_financial_data read_content"
    }

    # create session instance
    session = requests.Session()

    auth_request = session.post("https://idfs.gs.com/as/token.oauth2", data=auth_data)
    # print('Response {}'.format(auth_request.text))

    access_token_dict = json.loads(auth_request.text)
    access_token = access_token_dict["access_token"]

    # print('Access Token {}'.format(access_token))

    # update session headers with access token
    session.headers.update({"Authorization": "Bearer " + access_token})

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

    companies_list = [x[2] for x in companies_set]
    companies_dict = {x[2]: x[0] for x in companies_set}
    data_list = []
    for cp in companies_list:
        request_query = {
            "where": {
                "gsid": [cp]
            },
            "startDate": START_DATE.isoformat(),
            # "endDate":'2018-01-15'
        }

        request = session.post(url=request_url, json=request_query)
        results = json.loads(request.text)
        print('{} - {}'.format(companies_dict[cp], len(results['data'])))

        for entry in results['data']:
            entry['ticker'] = companies_dict[cp]
        data_list.append({'company': companies_dict[cp], 'data': results['data']})

    print('Total number of companies: {}'.format(len(data_list)))
    json.dump(data_list, open('companies_data.json', 'w'), indent=2)
    # print(data)

    ###### Graphing #######

    # 'growthScore': 0.234, 'multipleScore': 0.076, 'gsid': '901237', 'financialReturnsScore': 0.71,'c': 0.624

    return companies_set

def correlation_calculations():
    with open('companies_data.json') as data_file:
        company_data = json.load(data_file)

    stats = ['growthScore', 'multipleScore', 'financialReturnsScore', 'integratedScore']

    maxLen = 0
    for entry in company_data:
        maxLen = max(maxLen, len(entry['data']))

    companies = []
    for entry in company_data:
        if len(entry['data']) == maxLen:
            companies.append(entry['company'])

    print('Number of entires per company = {}'.format(maxLen))
    print('Number of companies with full set of entries = {}'.format(len(companies)))

    company_stats = {company: {stat: [] for stat in stats} for company in companies}
    company_FOD_stats = {company: {stat: [] for stat in stats} for company in companies}

    X = {company: 0 for company in companies}
    days = {company: [] for company in companies}

    for data_point in company_data:
        company_time_series = data_point["data"]
        if len(company_time_series) == maxLen:
            for entry in company_time_series:
                #print(entry)
                comp = entry['ticker']
                for stat in stats:
                    if stat in entry.keys():
                        company_stats[comp][stat].append(entry[stat])
                    else:
                        print('key error: {}, {}, {}'.format(comp, X[comp], stat))
                        company_stats[comp][stat].append(company_stats[comp][stat][-1])

                num_days = (date(*(int(a) for a in entry['date'].split('-'))) - START_DATE).days
                days[comp].append(num_days)
                X[comp] += 1

                # if len(days[comp]) >= 2 and days[comp][-1] != days[comp][-2] + 1:
                #     print('RIPPPP: {}, {}'.format(comp, days[comp][-1]))
                #     assert False

                if X[comp] > 1:
                    for stat in stats:
                        company_FOD_stats[comp][stat].append(company_stats[comp][stat][X[comp] - 1] - company_stats[comp][stat][X[comp] - 2])

    #print({comp: len(growthScores[comp]) for comp in companies})

    for stat in stats:
        print()
        print('Correlations for FOD {}'.format(stat))
        for f_company in companies:
            for s_company in companies:
                # print(f_company, s_company)
                # print('lengths of stat arrays: {}, {}'.format(len(company_FOD_stats[f_company]['growthScore']), len(company_FOD_stats[s_company]['growthScore'])))
                c = np.corrcoef(company_FOD_stats[f_company][stat], company_FOD_stats[s_company][stat])[0, 1]
                if c > 0.5 and f_company != s_company:
                    print(f_company, s_company, c)

    correlations = []
    #print(np.corrcoef(F0D_finReturnScores['AAPL'], F0D_finReturnScores['FB'])[0, 1])


    plt.plot(range(X['KORS'] - 1), company_FOD_stats['KORS']['financialReturnsScore'], color="green")
    plt.plot(range(X['LULU'] - 1), company_FOD_stats['LULU']['financialReturnsScore'], color="blue")

    plt.show()
    # algorithm - take differences. take corrcoef of that. figure out if first 75 matters (perhaps break it up).
#
# print(request_data())
correlation_calculations()
