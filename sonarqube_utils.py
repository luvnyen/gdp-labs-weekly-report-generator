import requests
from config import SONARQUBE_USER_TOKEN, SONARQUBE_API_URL, SONARQUBE_COMPONENT

def get_test_coverage():
    params = {
        'component': SONARQUBE_COMPONENT,
        'metricKeys': 'coverage'
    }

    headers = {
        'accept': 'application/json',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
    }

    auth = (SONARQUBE_USER_TOKEN, '')

    response = requests.get(SONARQUBE_API_URL, params=params, headers=headers, auth=auth)

    if response.status_code == 200:
        json_response = response.json()
        measures = json_response.get('component', {}).get('measures', [])
        coverage = next((measure['value'] for measure in measures if measure['metric'] == 'coverage'), None)
        return coverage
    else:
        print(f"Request failed with status code: {response.status_code}")
        print(response.text)
        return None