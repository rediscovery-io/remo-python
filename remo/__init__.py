from .domain import task, class_encodings, Dataset, Image, Annotation, AnnotationSet, Bbox, Segment
from .sdk import SDK
from .version import __version__

_sdk = None


def connect():
    """
    Connect to a local running remo server.
    
    """
    from .config import Config
    config = Config.load()
    connect_sdk(config.server_url(), config.user_email, config.user_password, config.viewer)


def connect_sdk(server: str, email: str, password: str, viewer: str = 'browser'):
    """
    Connect to a remote running remo server.
    
    Args:
        server: address where remo is running
        email:  email address used for authentication
        password: password used for authentication
        (optional) viewer: viewer to use, one between 'browser', 'electron' and 'jupyter'
    """
    global _sdk
    _sdk = SDK(server, email, password, viewer)
    # set access to public SDK methods
    import sys

    is_public_sdk_method = lambda name: not name.startswith('_') and callable(getattr(_sdk, name))
    functions = filter(is_public_sdk_method, dir(_sdk))
    for name in functions:
        setattr(sys.modules[__name__], name, getattr(_sdk, name))

try:
    connect()
except:
    pass