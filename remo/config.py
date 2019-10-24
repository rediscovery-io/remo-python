import json
import os


class Config:
    __slots__ = ['port', 'user_name', 'user_email', 'user_password']
    _default_port = 8000
    _default_user_name = 'Admin User'
    _default_user_email = 'admin@remo.ai'
    _default_user_password = 'adminpass'

    def __init__(self, config: dict):
        self.port = config.get('port', self._default_port)
        user = config.get('user', {})
        if user and type(user) is dict:
            self.user_name = user.get('name', self._default_user_name)
            self.user_email = user.get('email', self._default_user_email)
            self.user_password = user.get('password', self._default_user_password)


def parse_config(config_path) -> Config:
    if not os.path.exists(config_path):
        return None

    with open(config_path) as cfg_file:
        config = json.load(cfg_file)

    return Config(config)
