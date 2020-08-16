import json
import os
from pathlib import Path

REMO_HOME_ENV = 'REMO_HOME'


def REMO_HOME():
    return os.getenv(REMO_HOME_ENV, str(Path.home().joinpath('.remo')))


def set_REMO_HOME(path: str):
    if not os.path.exists(path):
        os.makedirs(path)
    os.environ[REMO_HOME_ENV] = path


class Config:
    """
    Remo Config

    This class is used to initialise various settings.
    #TODO: add description of how those are initiliased from code vs from config file
    """
    __slots__ = ['port', 'server', 'user_name', 'user_email', 'user_password', 'viewer']
    _default_port = 8123
    _default_server = 'http://localhost'
    _default_user_name = 'Admin User'
    _default_user_email = 'admin@remo.ai'
    _default_user_password = 'adminpass'
    _default_viewer = 'browser'

    def __init__(self, config):
        for name in self.__slots__:
            setattr(self, name, config.get(name, getattr(self, '_default_{}'.format(name))))

    def server_url(self):
        return '{}:{}'.format(self.server, self.port)

    @staticmethod
    def load(config_path: str = str(os.path.join(REMO_HOME(), 'remo.json'))):
        if not os.path.exists(config_path):
            return None

        with open(config_path) as cfg_file:
            config = json.load(cfg_file)

        return Config(config)
