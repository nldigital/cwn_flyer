#!/usr/bin/env python3

import datetime
import json
import requests
from collections import namedtuple


OpenHsvEvent = namedtuple('OpenHsvEvent', ['name', 'date', 'location'])
OpenHsvSession = namedtuple('OpenHsvSession',
                            ['time_req', 'date', 'end_time', 'approved',
                             'group', 'category', 'start_time', 'title',
                             'time_req_form', 'timestamp',
                             'room_req', 'cwn', 'icon', 'description'])


def to_datetime(openhsv_time, format="%Y-%m-%dT%H:%M:%S"):
    return datetime.datetime.strptime(openhsv_time.split('.')[0], format)


class OpenHsvApi(object):
    def __init__(self, base_url='http://www.openhuntsville.com/api/v1/'):
        self.base_url = base_url

    def init_app(self, app):
        if 'BASE_URL' in app.config:
            self.base_url = app.config['BASE_URL']

    def query(self, route):
        return json.loads(requests.get(
            self.base_url + route).content.decode('utf-8'))

    def all_cwn_events(self):
        raw_events = self.query('all_cwn_events')
        events = []
        for e in raw_events:
            event = OpenHsvEvent(e['name'],
                                 to_datetime(e['date']),
                                 e['location'])
            events.append(event)
        return sorted(events, key=lambda event: event.date)

    def _current_week_idx(self):
        events = self.all_cwn_events()
        now = datetime.datetime.utcnow()

        def time_diff(v):
            (idx, event) = v
            end_time = event.date + datetime.timedelta(hours=5)
            if end_time < now:
                return datetime.timedelta(days=1e6)
            else:
                return end_time - now
        return events, min(enumerate(events), key=time_diff)[0]

    def current_week(self):
        events, idx = self._current_week_idx()
        return events[idx]

    def current_week_id(self):
        '''
        This is such a hack, but I don't get an ID
        '''
        events, idx = self._current_week_idx()
        return int(events[idx].name.split('#')[1])

    def next_week(self):
        events, idx = self._current_week_idx()
        return events[idx+1]

    def next_week_id(self):
        '''
        This is such a hack, but I don't get an ID
        '''
        events, idx = self._current_week_idx()
        return int(events[idx+1].name.split('#')[1])

    def get_event_sessions(self, id):
        raw_sessions = self.query('cwn_flyer/%i' % id)
        sessions = []
        for rs in raw_sessions:
            session = OpenHsvSession(
                to_datetime(rs['time_req']),
                to_datetime(rs['date']),
                to_datetime(rs['end_time']),
                rs['approved'],
                rs['group'],
                rs['category'],
                to_datetime(rs['start_time']),
                rs['title'],
                to_datetime(rs['time_req_form']),
                to_datetime(rs['timestamp']),
                rs['room_req'],
                rs['cwn'],
                rs['icon'],
                rs['description'])
            sessions.append(session)
        return sessions


if __name__ == "__main__":
    api = OpenHsvApi()
    api.all_cwn_events()
    api.get_event_sessions(123)
    print(api.current_week())
    print(api.next_week())
    print(api.current_week_id())



