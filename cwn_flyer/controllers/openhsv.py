
from flask import Blueprint, render_template, flash, request, redirect, url_for, abort, jsonify
from flask import current_app
from flask import Flask

from urllib.request import urlopen
import simplejson
import json

import datetime
import pytz

from collections import OrderedDict

import httplib2
import os

openhsv = Blueprint('openhsv', __name__)

TIME_SLOTS = [
        datetime.time(17, 00, 00),
        datetime.time(17, 30, 00),
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
05/24/2017	106
05/31/2017      107
06/07/2017	108
06/14/2017	109
06/21/2017	110
06/28/2017	111
07/05/2017      112
07/12/2017	113
07/19/2017	114
07/26/2017	115
08/02/2017	116"""

CWN = OrderedDict()

for line in CWN_TEXT.split('\n'):
    entries = line.split('\t')
    CWN[int(entries[1])] = datetime.datetime.strptime(entries[0],"%m/%d/%Y")

@openhsv.app_template_filter('pretty_time')
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

def get_events(weekno):
    events = []  
    try:
        req = urlopen("http://www.openhuntsville.com/api/v1/cwn_flyer/" + str(weekno), timeout=1).read().decode('utf-8')
    except:
        return events 
    events = json.loads(req)
    events_parsed = []
    utc = pytz.timezone("UTC")
    local = pytz.timezone("America/Chicago")
    for event in events:
        if event['approved'] == True:
            event['start_time'] = datetime.datetime.strptime(event['start_time'], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=utc).astimezone(local)
            event['end_time'] = datetime.datetime.strptime(event['end_time'], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=utc).astimezone(local)
            events_parsed.append(event)
    return events_parsed


def make_schedule(weekno):
    current_app.logger.info('Rendering schedule for event %s'%str(weekno))
    events = get_events(weekno)
    filtered_results = OrderedDict()
    utc = pytz.timezone("UTC")
    local = pytz.timezone("America/Chicago")

    for slot in TIME_SLOTS:
        filtered_results[slot] = []

    for item in events:
        print( item['cwn'], weekno)
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

    meta = []
    meta.append('<meta property="og:title" content="Coworking Night #%i" />')
    meta.append('<meta property="og:type" content="event" />')
    meta.append('<meta property="og:url" content="http://atcwn.nld.to" />')
    meta.append('<meta property="og:description" content="CoWorking Night is a free weekly conference where professionals come to learn, connect, and collaborate.  Each week features a new lineup of workshops.  See what\'s happening this week!" />') 
    meta.append('<meta property="og:site_name" content="CoWorking Night" />')
    meta = '\n'.join(meta)

    print(CWN)

    return render_template('index.html', slotted_events=filtered_results, weekno=weekno, date=CWN[weekno], title="CoWorking Night Flyer #%i"%weekno, metadata=meta)

def current_week():
    today = datetime.date.today()
    for cwn, date in CWN.items():
        if today > (date.date() + datetime.timedelta(days=1)):
            continue
        else:
            return cwn

def next_week():
    return current_week() + 1


def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)

def links():
    links = []
    for rule in current_app.url_map.iter_rules():
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            links.append((url, rule.endpoint))
    return links


@openhsv.route('/site-map')
def site_map():
    return jsonify(links())
    

@openhsv.route('/schedule', methods=['GET'])
def schedule():
    return make_schedule(current_week())

@openhsv.route('/schedule/<event_id>', methods=['GET'])
def schedule_event(event_id):
    current_app.logger.info('Rendering schedule for event %s'%str(event_id))
    if event_id == "current":
        return make_schedule(current_week())
    if event_id == "next":
        return make_schedule(next_week())
    return make_schedule(int(event_id))

@openhsv.route('/', methods=['GET'])
def home():
    current_app.logger.info(links())
    return make_schedule(current_week())

