import os
from cwn_flyer import create_app

app = create_app(os.environ.get('APP_CONFIG', 'cwn_flyer.config.ProductionConfig'))
