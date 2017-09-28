import os
import click
from flask.cli import FlaskGroup

def create_flyer_app(info):
    from cwn_flyer import create_app
    return create_app(os.environ.get('APP_CONFIG', 'cwn_flyer.config.ProductionConfig'))

@click.group(cls=FlaskGroup, create_app=create_flyer_app)
def cli():
    pass

if __name__ == '__main__':
    cli()
