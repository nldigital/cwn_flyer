#!/usr/bin/env python3
import sys
import os

from cwn_flyer import create_app

env = os.environ.get('ENV', 'prod')
app = create_app('cwn_flyer.settings.ProdConfig', env=env)
application = app

if __name__ == "__main__":
    app.run()
