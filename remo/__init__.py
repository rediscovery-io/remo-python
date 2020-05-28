from .domain import task, class_encodings, Dataset, Image, Annotation, AnnotationSet, Bbox, Segment
from .sdk import SDK
from .version import __version__

_sdk = None


def init():
    from .config import Config
    config = Config.load()
    init_sdk(config.server_url(), config.user_email, config.user_password)


def init_sdk(server: str, email: str, password: str, viewer: str = 'browser'):
    global _sdk
    _sdk = SDK(server, email, password, viewer)
    # set access to public SDK methods
    import sys

    is_public_sdk_method = lambda name: not name.startswith('_') and callable(getattr(_sdk, name))
    functions = filter(is_public_sdk_method, dir(_sdk))
    for name in functions:
        setattr(sys.modules[__name__], name, getattr(_sdk, name))

try:
    init()
except:
    pass