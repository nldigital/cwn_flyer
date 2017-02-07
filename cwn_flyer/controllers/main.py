
from flask import Blueprint, render_template, flash, request, redirect, url_for, abort, jsonify
from flask import current_app

import urllib
import simplejson

import datetime
import pytz

from collections import OrderedDict

from cwn_flyer.extensions import cache

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
03/01/2017	95
03/08/2017	96
03/15/2017	97
03/22/2017	98
03/29/2017	99
04/05/2017	100
04/12/2017	101
04/19/2017	102
04/26/2017	103
05/03/2017	104
05/10/2017	105
05/17/2017	106
05/24/2017	107"""

CWN = OrderedDict()

for line in CWN_TEXT.split('\n'):
    entries = line.split('\t')
    CWN[int(entries[1])] = datetime.datetime.strptime(entries[0],"%m/%d/%Y")
print(CWN)

@main.app_template_filter('pretty_time')
def _jinja2_filter_datetime(input, fmt=None):
    if type(input) != datetime.time:
        if type(input) == datetime.datetime:
            date = input
        elif type(input) == str:
            date = datetime.datetime.strptime(input.split('.')[0], "%Y-%m-%dT%H:%M:%S")
        time = pytz.utc.localize(date).astimezone(pytz.timezone('America/Chicago')).time()
    else:
        time = input
    format='%I:%M %p'
    s = time.strftime(format)
    if s[0] == '0':
        s = s[1:]
    return s

@cache.cached(timeout=1000)
def make_schedule(weekno):
    QUERY_URL="https://script.google.com/macros/s/AKfycbxDCvI79Q_lV8EHvirA-t44q6pbDkPi1hdMWE3jH73wVaDxH1A/exec"
    result = simplejson.load(urllib.request.urlopen(QUERY_URL))
    filtered_results = OrderedDict()
    utc = pytz.timezone("UTC")
    local = pytz.timezone("America/Chicago")

    for slot in TIME_SLOTS:
        filtered_results[slot] = []

    for item in result:
        if item['cwn'] == weekno:
            for slot in TIME_SLOTS:
                dt = datetime.datetime.strptime(item['start_time'].split('.')[0], "%Y-%m-%dT%H:%M:%S")
                time = utc.localize(dt).astimezone(local).time()
                if time == slot:
                    filtered_results[slot].append(item)

    to_del = []
    for key, val in filtered_results.items():
        if len(val) == 0:
            to_del.append(key)

    for key in to_del:
        del filtered_results[key]

    return render_template('index.html', slotted_events=filtered_results, weekno=weekno, date=CWN[weekno])

def current_week():
    today = datetime.date.today()
    for cwn, date in CWN.items():
        print(today, date.date(), today < date.date(), cwn)

        if today > date.date():
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
        print("current")
        return make_schedule(current_week())
    if event_id == "next":
        print("next")
        return make_schedule(next_week())
    return make_schedule(int(event_id))






