from .domain import task, class_encodings, Dataset, Image, Annotation, AnnotationSet, Bbox, Segment
from .sdk import SDK
from .version import __version__

_sdk = None


def connect(server: str = '', email: str = '', password: str = '', viewer: str = 'browser', remo_home: str = None):
    """
    Connect to a remo server.
    If no parameters are passed, it connects to a local running remo server. To connect to a remote remo, specify connection details.
    
    Args:
        server: address where remo is running
        email:  email address used for authentication
        password: password used for authentication
        (optional) viewer: viewer to use, one between 'browser', 'electron' and 'jupyter'
        (optional) remo_home: location of remo home
    """

    if remo_home:
        from .config import set_remo_home
        set_remo_home(remo_home)

    if not (server and email and password):
        from .config import Config
        config = Config.load()
        server, email, password, viewer = config.server_url(), config.user_email, config.user_password, config.viewer

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
    print("""Warning: Can't find a running remo app. 
To start a local server: 'python -m remo_app' and then run remo.connect(). 
You can also use 'remo.connect()' to connect to a remote server""")
