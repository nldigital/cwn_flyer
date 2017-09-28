"""
OpenHSV. Copyright New Leaf Digital 2017
"""

import datetime
import json
import requests
from collections import OrderedDict
import hashlib
import pytz

from flask import Blueprint, render_template, url_for, jsonify
from flask import current_app, Response, abort, redirect
from cwn_flyer import api


openhsv = Blueprint('openhsv', __name__)

def make_schedule(weekno):
    """
    Make a schedule for a given week
    """
    current_app.logger.info('Rendering schedule for event %s' % str(weekno))
    events = api.all_cwn_events()

    this_event = None
    for event in events:
        if event.name.find(str(weekno)) > 0:
            this_event = event
    if this_event is None:
        current_app.logger.info('Could not find weekno %s' % str(weekno))
        abort(404)

    sessions = api.get_event_sessions(weekno)
    time_slots = {}
    for item in sessions:
        time = item.start_time
        if time not in time_slots:
            time_slots[time] = []
        time_slots[time].append(item)

    time_slots_ord = OrderedDict()
    for t in sorted(time_slots.keys()):
        time_slots_ord[t] = time_slots[t]

    hashval = hashlib.md5(("http://atcwn.nld.to/schedule/%i%s" %
                           (weekno, "PANCAKES")).encode('utf-8')).hexdigest()

    return render_template('index.html',
                           slotted_events=time_slots_ord,
                           weekno=weekno,
                           date=this_event.date,
                           title="CoWorking Night Flyer #%i" % weekno,
                           hashval=hashval)

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

@openhsv.route('/robots.txt')
def robots_txt():
    """
    Serve up robots for google
    """
    vals = []
    vals.append('Sitemap: http://atcwn.nld.to/sitemap.txt')
    return "\n".join(vals)


@openhsv.route('/schedule', methods=['GET'])
def schedule():
    """
    Get a copy of the schedule for the current week
    """
    return redirect(url_for('openhsv.schedule_event', event_id=api.current_week_id()))


@openhsv.route('/schedule/current', methods=['GET'])
def current_schedule():
    return redirect(url_for('openhsv.schedule_event', event_id=api.current_week_id()))

@openhsv.route('/schedule/next', methods=['GET'])
def next_schedule():
    return redirect(url_for('openhsv.schedule_event', event_id=api.next_week_id()))

@openhsv.route('/schedule/<int:event_id>', methods=['GET'])
def schedule_event(event_id):
    """
    Get a copy of the schedule for an identified week
    """
    current_app.logger.info('Rendering schedule for event %s' % str(event_id))
    return make_schedule(event_id)


@openhsv.route('/', methods=['GET'])
def home():
    """
    Render home page
    """
    return redirect(url_for('openhsv.schedule_event', event_id=api.current_week_id()))
