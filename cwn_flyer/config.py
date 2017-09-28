class BaseConfig(object):
    SECRET_KEY = 'asdfasdfasdfasdf'


class ProductionConfig(BaseConfig):
    DEBUG = False


class DevevelopConfig(BaseConfig):
    DEBUG = True


class TestConfig(BaseConfig):
    DEBUG = True

