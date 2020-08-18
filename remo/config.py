import json
import os
from pathlib import Path

REMO_HOME_ENV = 'REMO_HOME'
default_remo_home = str(Path.home().joinpath('.remo'))
default_colab_remo_home = '/gdrive/My Drive/RemoApp'


def get_remo_home():
    for path in (os.getenv(REMO_HOME_ENV, default_remo_home), default_colab_remo_home):
        if path and os.path.exists(path):
            return path


def set_remo_home(path: str):
    os.makedirs(path, exist_ok=True)
    os.environ[REMO_HOME_ENV] = path


def set_remo_home_from_default_remo_config() -> bool:
    if os.path.exists(Config.default_path()):
        config = Config.load(Config.default_path())
        if config and config.remo_home:
            set_remo_home(config.remo_home)
            return True


class Config:
    """
    Remo Config

    This class is used to initialise various settings.
    #TODO: add description of how those are initiliased from code vs from config file
    """

    name = 'remo.json'
    __slots__ = [
        'port',
        'server',
        'user_name',
        'user_email',
        'user_password',
        'viewer',
        'uuid',
        'public_url',
        'remo_home',
        'cloud_platform',
    ]
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
    def load(config_path: str = None):
        if not config_path:
            config_path = str(os.path.join(get_remo_home(), Config.name))

        if not os.path.exists(config_path):
            raise Exception(f'Config file not found, file {config_path} not exists')

        with open(config_path) as cfg_file:
            config = json.load(cfg_file)

        return Config(config)

    @staticmethod
    def default_path():
        return Config.path(default_remo_home)

    @staticmethod
    def path(dir_path: str = None):
        if not dir_path:
            dir_path = get_remo_home()
        return str(os.path.join(dir_path, Config.name))