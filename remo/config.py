import json
import os


class Config:
    __slots__ = ['port', 'server', 'user_name', 'user_email', 'user_password', 'conda_env', 'viewer']
    _default_port = 8000
    _default_server = 'http://localhost'
    _default_user_name = 'Admin User'
    _default_user_email = 'admin@remo.ai'
    _default_user_password = 'adminpass'
    _default_viewer = 'browser'

    def __init__(self, config):
        self.port = config.get('port', self._default_port)
        self.server = config.get('server', self._default_server)

        self.user_name = config.get('user_name', self._default_user_name)
        self.user_email = config.get('user_email', self._default_user_email)
        self.user_password = config.get('user_password', self._default_user_password)

        self.conda_env = config.get('conda_env')
        self.viewer = config.get('viewer', self._default_viewer)


def parse_config(config_path):
    if not os.path.exists(config_path):
        return None

    with open(config_path) as cfg_file:
        config = json.load(cfg_file)

    return Config(config)
