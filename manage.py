#!/usr/bin/env python3

import os

from flask.ext.script import Manager, Server
from flask.ext.script.commands import ShowUrls, Clean
from flask.ext.assets import ManageAssets

from cwn_flyer import assets_env
from cwn_flyer import create_app

# default to dev config because no one should use this in
# production anyway
env = os.environ.get('APPNAME_ENV', 'prod')
app = create_app('cwn_flyer.settings.%sConfig' % env.capitalize(), env=env)

manager = Manager(app)
manager.add_command("assets", ManageAssets(assets_env))
manager.add_command("server", Server())
manager.add_command("show-urls", ShowUrls())
manager.add_command("clean", Clean())


@manager.shell
def make_shell_context():
    """ Creates a python REPL with several default imports
        in the context of the app
    """
    return dict(app=app, db=db, User=User)


if __name__ == "__main__":
    manager.run()
