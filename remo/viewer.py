import os
import re
import platform
import subprocess
from abc import abstractmethod, ABCMeta
import webbrowser
import uuid

from remo.config import get_remo_home


class AbstractViewer(metaclass=ABCMeta):
    @abstractmethod
    def browse(self, url: str):
        raise NotImplementedError()


class JupyterViewer(AbstractViewer):

    def browse(self, url: str):
        print('Open', url)
        id = 'remo_frame_{}'.format(uuid.uuid4())
        url = self._headless(url)
        return self._html(id, url)

    @staticmethod
    def _headless(url: str) -> str:
        separator = '&' if '?' in url else '?'
        return '{}{}allheadless'.format(url, separator)

    @staticmethod
    def _html(id: str, url: str):
        from IPython.display import HTML
        return HTML("""
        <iframe
            id="{id}"
            width="100%"
            height="100px"
            src="{url}"
            frameborder="0"
            allowfullscreen
        ></iframe>""".format(id=id, url=url) + """
        <script type="text/javascript">
            (function () {""" + """
                const iframe = document.getElementById("{id}");
                let timeout, delay = 100;
            """.format(id=id) + """
                const setHeight = () => {
                  const width = iframe.clientWidth;
                  iframe.style.height = (width * screen.height / screen.width) * 0.8 + 'px';
                }
                window.addEventListener("resize", () => {
                    clearTimeout(timeout);
                  // start timing for event "completion"
                  timeout = setTimeout(setHeight, delay);
                });
                setHeight();
            })()
        </script>
        """)


class BrowserViewer(AbstractViewer):
    def browse(self, url: str):
        print('Open', url)
        webbrowser.open_new_tab(url)


class ElectronViewer(AbstractViewer):
    exe_path = {'Linux': 'app/remo', 'Darwin': 'app/remo.app/Contents/MacOS/remo', 'Windows': 'app/remo.exe'}
    url_rxp = re.compile(r'(http[s]?://[.\w-]+)(:([0-9]+))?/?(.+)?')

    def browse(self, url):
        print('Open', url)
        host, port, page = self.split_ulr(url)
        remo = self.get_remo_path()
        cmd = self.build_cmd(remo, host=host, port=port, page=page)
        subprocess.Popen(cmd, shell=True)

    def split_ulr(self, url):
        host, _, port, page = self.url_rxp.match(url).groups()
        return host, port, page

    @staticmethod
    def build_cmd(executable, **kwargs):
        return '{} {}'.format(executable, ' '.join('--{}={}'.format(k, v) for k, v in kwargs.items() if v))

    def get_remo_path(self):
        return str(os.path.join(get_remo_home(), self.exe_path.get(platform.system())))


def factory(name: str):
    viewer = {'jupyter': JupyterViewer, 'browser': BrowserViewer, 'electron': ElectronViewer}.get(name)

    if viewer:
        return viewer()

    raise NotImplementedError('Viewer {} - not implemented'.format(name))


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