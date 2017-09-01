"""
OpenHSV. Copyright New Leaf Digital 2017
"""

import datetime
import json
from urllib.request import urlopen
from collections import OrderedDict
import hashlib
import pytz

from flask import Blueprint, render_template, url_for, jsonify
from flask import current_app, Response

strptime = datetime.datetime.strptime

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


@openhsv.app_template_filter('pretty_time')
def _jinja2_filter_datetime(filter_input):
    if type(filter_input) != datetime.time:
        if type(filter_input) == datetime.datetime:
            date = filter_input
        elif type(filter_input) == str:
            date = strptime(filter_input.split('.')[0],
                            "%Y-%m-%dT%H:%M:%S")
        time = date.time()
    else:
        time = filter_input
    fmt = '%I:%M %p'
    formatted_time = time.strftime(fmt)
    if formatted_time[0] == '0':
        formatted_time = formatted_time[1:]
    return formatted_time


def get_upcoming():
    """
    Retrieve list of upcoming CWN.
    """
    events = OrderedDict()
    try:
        req = urlopen("http://www.openhuntsville.com/api/v1/cwn_future/",
                      timeout=1).read().decode('utf-8')
    except:
        return events

    tmp_events = json.loads(req)
    for event in tmp_events:
        event['date'] = strptime(event['date'].split('.')[0],
                                 "%Y-%m-%dT%H:%M:%S")
        event['cwn'] = int(event['name'].split('#')[1])
        events[event['cwn']] = event
    return events


def get_events(weekno):
    """
    Retrieve list of events from openhuntsville api
    """
    events = []
    try:
        req = urlopen(("http://www.openhuntsville.com/api/v1/cwn_flyer/" +
                       str(weekno)), timeout=1).read().decode('utf-8')
    except:
        return events
    events = json.loads(req)
    events_parsed = []
    utc = pytz.timezone("UTC")
    local = pytz.timezone("America/Chicago")
    for event in events:
        fmt = "%Y-%m-%dT%H:%M:%S.%fZ"
        if event['approved']:
            start = event['start_time']
            start = strptime(start, fmt)
            start = start.replace(tzinfo=utc).astimezone(local)
            event['start_time'] = start

            end = event['end_time']
            end = strptime(end, fmt)
            end = end.replace(tzinfo=utc).astimezone(local)
            event['end_time'] = end
            events_parsed.append(event)
    return events_parsed


def make_schedule(weekno):
    """
    Make a schedule for a given week
    """
    current_app.logger.info('Rendering schedule for event %s' % str(weekno))
    events = get_events(weekno)
    filtered_results = OrderedDict()

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

    hashval = hashlib.md5(("http://atcwn.nld.to/schedule/%i%s" %
                           (weekno, "PANCAKES")).encode('utf-8')).hexdigest()

    CWN = get_upcoming()
    return render_template('index.html',
                           slotted_events=filtered_results,
                           weekno=weekno,
                           date=CWN[weekno]['date'],
                           title="CoWorking Night Flyer #%i" % weekno,
                           hashval=hashval)


def current_week():
    """
    Get the number of the current week
    """
    today = datetime.datetime.today()
    CWN = get_upcoming()
    for cwn, item in CWN.items():
        if today > (item['date'] + datetime.timedelta(days=1)):
            continue
        else:
            return cwn


def next_week():
    """
    Get the number of the next week
    """
    return current_week() + 1


def has_no_empty_params(rule):
    """
    Check if a route has empty params
    """
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


def links():
    """
    Get a list of available flask routes
    """
    routes = []
    for rule in current_app.url_map.iter_rules():
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            routes.append((url, rule.endpoint))
    return routes


@openhsv.route('/site-map')
def site_map():
    """
    Serve up site map for google
    """
    return jsonify(links())


@openhsv.route('/sitemap.txt')
def sitemap_txt():
    """
    Serve up site map for google
    """
    vals = []
    base = "http://atcwn.nld.to/"
    vals.append(base + "schedule")
    vals.append(base + "schedule/current")
    vals.append(base + "schedule/next")
    for val in CWN.keys():
        vals.append(base + "schedule/%i" % val)
    return "\n".join(vals)


@openhsv.route('/robots.txt')
def robots_txt():
    """
    Serve up robots for google
    """
    vals = []
    vals.append('Sitemap: http://atcwn.nld.to/sitemap.txt')
    return "\n".join(vals)

@openhsv.route('/upcoming', methods=['GET'])
def upcoming():
    return Response(str(get_upcoming()))


@openhsv.route('/schedule', methods=['GET'])
def schedule():
    """
    Get a copy of the schedule for the current week
    """
    return make_schedule(current_week())


@openhsv.route('/schedule/<event_id>', methods=['GET'])
def schedule_event(event_id):
    """
    Get a copy of the schedule for an identified week
    """
    current_app.logger.info('Rendering schedule for event %s' % str(event_id))
    if event_id == "current":
        return make_schedule(current_week())
    if event_id == "next":
        return make_schedule(next_week())
    return make_schedule(int(event_id))


@openhsv.route('/', methods=['GET'])
def home():
    """
    Render home page
    """
    current_app.logger.info(links())
    return make_schedule(current_week())

