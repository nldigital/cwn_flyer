
from flask import Blueprint, render_template, flash, request, redirect, url_for, abort, jsonify
from flask import current_app

import urllib
import simplejson

import datetime
import pytz

from collections import OrderedDict

from cwn_flyer.extensions import cache

import httplib2
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import os

main = Blueprint('main', __name__)

TIME_SLOTS = [
        datetime.time(18, 00, 00),
        datetime.time(18, 30, 00),
        datetime.time(19, 00, 00),
        datetime.time(19, 30, 00),
        datetime.time(20, 00, 00),
        datetime.time(20, 30, 00),
        datetime.time(21, 00, 00),
        datetime.time(21, 30, 00)]

CWN_TEXT = """12/07/2016	85
12/14/2016	86
01/04/2017	87
01/11/2017	88
01/18/2017	89
01/25/2017	90
02/01/2017	91
02/08/2017	92
02/15/2017	93
02/22/2017	94
03/08/2017	95
03/15/2017	96
03/22/2017	97
03/29/2017	98
04/05/2017	99
04/12/2017	100
04/19/2017	101
04/26/2017	102
05/03/2017	103
05/10/2017	104
05/17/2017	105
05/24/2017	106"""

CWN = OrderedDict()

for line in CWN_TEXT.split('\n'):
    entries = line.split('\t')
    CWN[int(entries[1])] = datetime.datetime.strptime(entries[0],"%m/%d/%Y")

@main.app_template_filter('pretty_time')
def _jinja2_filter_datetime(input, fmt=None):
    if type(input) != datetime.time:
        if type(input) == datetime.datetime:
            date = input
        elif type(input) == str:
            date = datetime.datetime.strptime(input.split('.')[0], "%Y-%m-%dT%H:%M:%S")
        time = date.time()
    else:
        time = input
    format='%I:%M %p'
    s = time.strftime(format)
    if s[0] == '0':
        s = s[1:]
    return s

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
        credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def get_events():
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

    new_events = []

    for event in events:
        event['approved'] = bool(event['approved'])
        event['cwn'] = int(event['cwn'])
        try:
            event['start_time'] = datetime.datetime.strptime(event['start_time'], "%m/%d/%Y %H:%M:%S")
        except:
            continue
        try:
            event['end_time'] = datetime.datetime.strptime(event['end_time'], "%m/%d/%Y %H:%M:%S")
        except:
            continue

        if event['icon'] == '':
            event['icon'] = 'pencil'
        else:
            event['icon'] = event['icon'].lower()
        new_events.append(event)
    return new_events



@cache.cached(timeout=1000)
def make_schedule(weekno):
    events = get_events()
    filtered_results = OrderedDict()
    utc = pytz.timezone("UTC")
    local = pytz.timezone("America/Chicago")

    for slot in TIME_SLOTS:
        filtered_results[slot] = []

    for item in events:
        if item['cwn'] == weekno:
            for slot in TIME_SLOTS:
                time = item['start_time'].time()
                if time == slot:
                    filtered_results[slot].append(item)
    to_del = []
    for key, val in filtered_results.items():
        if len(val) == 0:
            to_del.append(key)

    for key in to_del:
        del filtered_results[key]


    return render_template('index.html', slotted_events=filtered_results, weekno=weekno, date=CWN[weekno], title="CoWorking Night Flyer")

def current_week():
    today = datetime.date.today()
    for cwn, date in CWN.items():
        if today > (date.date() + datetime.timedelta(days=1)):
            continue
        else:
            return cwn

def next_week():
    return current_week() + 1

@main.route('/', methods=['GET'])
def home():
    return make_schedule(current_week())

@main.route('/schedule', methods=['GET'])
def schedule():
    return make_schedule(current_week())

@main.route('/schedule/<event_id>')
def schedule_event(event_id):
    if event_id == "current":
        return make_schedule(current_week())
    if event_id == "next":
        return make_schedule(next_week())
    return make_schedule(int(event_id))

