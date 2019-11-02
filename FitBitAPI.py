import requests
import json
import base64
import urllib3
import csv
from datetime import date, timedelta

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

authorize_url = 'https://www.fitbit.com/oauth2/authorize'
token_url = 'https://api.fitbit.com/oauth2/token'

client_id = ''
client_secret = ''
redirect_address = 'http://url.to/accept.php'

auth_filename = 'auth_key'
try:
    auth_file = open(auth_filename, 'r');
    auth_code = auth_file.read()
    auth_file.close()

except:
    auth_url = 'https://www.fitbit.com/oauth2/authorize?response_type=code&client_id={}&redirect_uri={}&fitbit_auth&scope=activity%20nutrition%20heartrate%20location%20nutrition%20profile%20settings%20sleep%20social%20weight'.format(client_id, redirect_address)
    print('Could not open auth_key file, ensure that authorization has been gotten from: \n' + auth_url)
    exit()


try:
    fh = open('refresh_key', 'r')
    refresh_token = fh.read()
    fh.close()
except FileNotFoundError:
    refresh_token = ''


if refresh_token == '':

    data = {'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': redirect_address}

else:

    data = {'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'redirect_uri': redirect_address}

auth_data = client_id + ':' + client_secret
encoded_auth = auth_data.encode()
encoded = base64.b64encode(encoded_auth)

access_token_response = requests.post(token_url,
                                      data=data,
                                      verify=False,
                                      allow_redirects=False,
                                      auth=(client_id, client_secret))

tokens = json.loads(access_token_response.text)
print(tokens)

access_token = tokens['access_token']
refresh_token = tokens['refresh_token']

fh = open('refresh_key', 'w')
fh.write(refresh_token)
fh.close()

today = date.today()
yesterday = today - timedelta(days=1)
date_str = yesterday.isoformat()

test_api_url = 'https://api.fitbit.com/1/user/-/activities/heart/date/{}/1d/1sec/time/00:00/23:59:59.json'.format(date_str)

api_call_headers = {'Authorization': 'Bearer ' + access_token}

api_call_response = requests.get(test_api_url,
                                 headers=api_call_headers,
                                 verify=False)

if api_call_response.status_code != 200:
    print('The API call was not OK, status: ' + str(api_call_response.status_code) + str(api_call_response.json()))
    exit()

print(api_call_response)

returned_data = json.loads(api_call_response.text)

print(returned_data['activities-heart-intraday']['dataset'])

with open(date_str + '.csv', 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file, delimiter=',',  quotechar='"', quoting=csv.QUOTE_MINIMAL)

    for reading in returned_data['activities-heart-intraday']['dataset']:
        reading['date'] = date_str

        temp_list = []

        for key, value in reading.items():
            temp_list.append(value)

        csv_writer.writerow(temp_list)
