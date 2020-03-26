import os
from .domain import task, class_encodings, Dataset, Image, Annotation, AnnotationSet

__version__ = '0.0.18'
_sdk = None
_logs = None
_server = None


def __init__(skip_sdk_init=os.getenv('REMO_SKIP_SDK_INIT', False)):
    if skip_sdk_init == 'True':
        return

    from pathlib import Path
    from .config import parse_config

    REMO_HOME = os.getenv('REMO_HOME', str(Path.home().joinpath('.remo')))
    cfg_path = str(os.path.join(REMO_HOME, 'remo.json'))
    config = parse_config(cfg_path)

    def is_jupyter_notebook():
        try:
            shell = get_ipython().__class__.__name__
            if shell == 'ZMQInteractiveShell':
                return True  # Jupyter notebook or qtconsole
            elif shell == 'TerminalInteractiveShell':
                return False  # Terminal running IPython
            else:
                return False  # Other type (?)
        except NameError:
            return False  # Probably standard Python interpreter

    if config:
       # viewer = 'jupyter' if is_jupyter_notebook() else config.viewer
        viewer = config.viewer
        server_url = '{}:{}'.format(config.server, config.port)

        def terminate_server():
            global _logs
            global _server
            print('Terminating Remo server')
            if _server:
                _server.terminate()
                _logs.close()

        def launch_server(open_browser=True):
            import time
            import requests
            from .viewer import BrowserViewer

            version_endpoint = '{}/version'.format(server_url)
            try:
                r = requests.get(version_endpoint).json()
                version = 'v{}'.format(r.get('version'))
                print(
                    """
    (\(\ 
    (>':') Remo server is running: {}
                """.format(
                        version
                    )
                )
                if open_browser:
                    BrowserViewer().browse('{}:{}'.format(config.server, config.port))

                return True
            except:
                pass

            print('Launching Remo server ...')

            if not os.path.exists(config.conda_env):
                print(
                    """
    WARNING: Provided conda environment does not exist at {}
    
    Failed to launch Remo server, please start it manually.
    
    To fix config issue, please run init or update for Remo server (inside Remo conda env), like: 
    python -m remo_app init
    or
    python -m remo_app update
    """.format(
                        config.conda_env
                    )
                )
                return False

            global _logs
            global _server
            _logs = open(str(os.path.join(REMO_HOME, 'logs.txt')), 'w')

            path_args = ['python'] if os.name == 'nt' else ['bin', 'python']
            python_exe = os.path.join(config.conda_env, *path_args)

            import subprocess

            _server = subprocess.Popen(
                '{} -m remo_app'.format(python_exe),
                stdout=_logs,
                stderr=_logs,
                shell=True,
                universal_newlines=True,
            )

            time.sleep(5)
            retry = 5
            while retry > 0:
                print('Wait a bit... ', retry)
                try:
                    resp = requests.get(version_endpoint)
                    print(
                        """
    (\(\ 
    (>':') Remo server is running: {}
                    """.format(
                            resp.json()
                        )
                    )
                    if open_browser:
                        BrowserViewer().browse(server_url)

                    return True
                except:
                    time.sleep(1)
                retry -= 1

            print('Failed to launch Remo server, please start it manually')
            return False

        launch_server(open_browser=False)
        global _sdk
        from .sdk import SDK

        _sdk = SDK(server_url, config.user_email, config.user_password, viewer)

        # set access to public SDK methods
        import sys

        is_public_sdk_method = lambda name: not name.startswith('_') and callable(getattr(_sdk, name))
        functions = filter(is_public_sdk_method, dir(_sdk))
        for name in functions:
            setattr(sys.modules[__name__], name, getattr(_sdk, name))

        setattr(sys.modules[__name__], 'launch_server', launch_server)
        setattr(sys.modules[__name__], 'terminate_server', terminate_server)

    else:
        print(
            """
        WARNING: Config not found in {}
        
        Please run init for Remo server (inside Remo conda env), like: 
        
        python -m remo_app init
        
        """.format(
                cfg_path
            )
        )


__init__()
