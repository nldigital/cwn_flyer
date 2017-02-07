class Config(object):
    SECRET_KEY = ('asdfasdfasdfasdf')

class ProdConfig(Config):
    DEBUG = False
    ASSETS_DEBUG = False
    CACHE_TYPE = 'simple'

class DevConfig(Config):
    DEBUG = True
    ASSETS_DEBUG = True
    CACHE_TYPE = 'simple'

class TestConfig(Config):
    DEBUG = True
    CACHE_TYPE = 'null'


