import requests
import json
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from datetime import date

START_DATE = date(2017, 1, 15)


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
    companies_set = {(result['ticker'], result['name']) for result in reference_data['results']}

    i = 0
    cp = [x[0] for x in companies_set]
    with open('companydata.json', 'w') as outfile:
        outfile.write('[\n')
        while i < len(cp) - 2:
            print(cp[i])
            cps = [cp[i]]
            request_query = {
                "where": {
                    "ticker": cps
                },
                "startDate": START_DATE.isoformat(),
                # "endDate":'2018-01-15'
            }

            request = session.post(url=request_url, json=request_query)
            results = json.loads(request.text)
            print(results)
            print()
            json_data = results
            json.dump(json_data, outfile)
            outfile.write(',\n')

            i += 1
        outfile.write(']')
    # print(data)

    ###### Graphing #######

    # 'growthScore': 0.234, 'multipleScore': 0.076, 'gsid': '901237', 'financialReturnsScore': 0.71,'c': 0.624

    return companies_set

def correlation_calculations():
    with open('companydata.json') as data_file:
        file = json.load(data_file)

    companies = []
    for i in range(len(file)):
        #print(file[i])
        if len(file[i]["data"]) > 0:
            companies.append(file[i]["data"][0]["ticker"])

    #print(companies)

    growthScores = {company: [] for company in companies}
    multipleScores = {company: [] for company in companies}
    finReturnScores = {company: [] for company in companies}
    intergratedScores = {company: [] for company in companies}
    X = {company: 0 for company in companies}
    F0D_growthScores = {company: [] for company in companies}
    F0D_multipleScores = {company: [] for company in companies}
    F0D_finReturnScores = {company: [] for company in companies}
    F0D_intergratedScores = {company: [] for company in companies}
    days = {company: [] for company in companies}

    for data_point in file:
        company_time_series = data_point["data"]
        if len(company_time_series) > 0:
            if company_time_series[0]['ticker'] not in ['GPS', 'ULTI', 'ADS', 'MO', 'UNFI', 'CSOD', 'GRPN']:
                #print(company_time_series[0]['ticker'])
                for entry in company_time_series:
                    #print(entry)
                    comp = entry['ticker']
                    growthScores[comp].append(entry['growthScore'])
                    multipleScores[comp].append(entry['multipleScore'])
                    finReturnScores[comp].append(entry['financialReturnsScore'])
                    intergratedScores[comp].append(entry['integratedScore'])
                    X[comp] += 1
                    num_days = (date(*(int(a) for a in entry['date'].split('-'))) - START_DATE).days
                    days[comp].append(num_days)

                    if len(days[comp]) >= 2 and days[comp][-1] <= days[comp][-2]:
                        print('RIPPPP')
                        assert False

                    if X[comp] > 1:
                        F0D_growthScores[comp].append(growthScores[comp][X[comp] - 1] - growthScores[comp][X[comp] - 2])
                        F0D_multipleScores[comp].append(multipleScores[comp][X[comp] - 1] - multipleScores[comp][X[comp] - 2])
                        F0D_finReturnScores[comp].append(
                            finReturnScores[comp][X[comp] - 1] - finReturnScores[comp][X[comp] - 2])
                        F0D_intergratedScores[comp].append(
                            intergratedScores[comp][X[comp] - 1] - intergratedScores[comp][X[comp] - 2])

    #print({comp: len(growthScores[comp]) for comp in companies})

    for f_company in set(companies) - {'GPS', 'ULTI', 'ADS', 'MO', 'UNFI', 'CSOD', 'GRPN'}:
        for s_company in set(companies) - {'GPS', 'ULTI', 'ADS', 'MO', 'UNFI', 'CSOD', 'GRPN'}:
            #print(f_company, s_company)
            #print(F0D_finReturnScores[f_company])
            #print(F0D_finReturnScores[s_company])
            c = np.corrcoef(F0D_intergratedScores[f_company], F0D_intergratedScores[s_company])[0, 1]
            if abs(c) > 0.8 and f_company != s_company:
                print(f_company, s_company, c)
            #print()

    correlations = []
    #print(np.corrcoef(F0D_finReturnScores['AAPL'], F0D_finReturnScores['FB'])[0, 1])


    plt.plot(range(X['KORS'] - 1), F0D_finReturnScores['KORS'], color="green")
    plt.plot(range(X['LULU'] - 1), F0D_finReturnScores['LULU'], color="blue")

    plt.show()
    # algorithm - take differences. take corrcoef of that. figure out if first 75 matters (perhaps break it up).
#
#data, companies, cs = request_data()
correlation_calculations()
