from flask.ext.cache import Cache
from flask.ext.debugtoolbar import DebugToolbarExtension
from flask_assets import Environment

cache = Cache()
assets_env = Environment()
debug_toolbar = DebugToolbarExtension()

