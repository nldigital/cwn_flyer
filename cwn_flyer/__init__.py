#! /usr/bin/env python3

import os

from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from flask_moment import Moment

from cwn_flyer.openhsv_api import OpenHsvApi

toolbar = DebugToolbarExtension()
moment = Moment()
api = OpenHsvApi()

def create_app(object_name="cwn_flyer.config.ProductionConfig"):
    app = Flask(__name__)
    app.config.from_object(object_name)

    toolbar.init_app(app)
    moment.init_app(app)
    api.init_app(app)

    from cwn_flyer.views import openhsv
    app.register_blueprint(openhsv)

    return app
