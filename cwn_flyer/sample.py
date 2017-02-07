#!/usr/bin/env python3

import httplib2
import os
from apiclient import discovery

import datetime

from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = 'client_secret_476542259117-ci56njtr3vkckmfl6so2e9l4pr7s6n3o.apps.googleusercontent.com.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

if __name__ == "__main__":
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    spreadsheetId = '1cNePpbnqO0slG7FNyGD08EEJv-ihjp3KPSD-IRejrAw'
    rangeName = 'Events!A:R'
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName).execute()

    values = result.get('values', [])
    index_map = {
            'approved': 0,
            'cwn': 1,
            'req_stamp': 2,
            'group': 3,
            'title': 4,
            'description': 5,
            'category': 6,
            'icon':7,
            'date_req': 8,
            'start_time_req': 9,
            'room_req': 11,
            'resources': 12,
            'series': 13,
            'duration': 15,
            'start_time': 16,
            'end_time': 17,
            }

    events = []
    for row in values[1:]:
        if(len(row) < 18):
            continue
        event = {}
        for k in index_map.keys():
            event[k] = row[index_map[k]]
        if event['approved'] == 'TRUE':
            events.append(event)

    for event in events:
        event['approved'] = bool(event['approved'])
        event['cwn'] = int(event['cwn'])
        event['start_time'] = datetime.datetime.strptime(event['start_time'], "%m/%d/%Y %H:%M:%S")
        event['end_time'] = datetime.datetime.strptime(event['end_time'], "%m/%d/%Y %H:%M:%S")

    print(events)
