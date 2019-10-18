import os
import webbrowser

IMAGE_EXTENSIONS = {'.jpeg', '.jpg', '.png', '.tiff', '.tif'}
ANNOTATION_EXTENSIONS = {'.csv', '.xml', '.json'}
ARCHIVE_EXTENSIONS = {'.zip', '.tar', '.gz', '.bz2'}


def file_extension(name):
    return os.path.splitext(name)[1].lower()


def is_image_file(name):
    ext = file_extension(name)
    return ext in IMAGE_EXTENSIONS


def is_annotation_file(name):
    ext = file_extension(name)
    return ext in ANNOTATION_EXTENSIONS


def is_archive_file(name):
    ext = file_extension(name)
    return ext in ARCHIVE_EXTENSIONS


def is_ignored_file(name):
    return name.startswith('.')


def resolve_path(path):
    return os.path.realpath(os.path.abspath(path))


class FileResolver:
    def __init__(self, files, with_annotations=False):
        self.images = set()
        self.annotations = set()
        self.archives = set()
        self.files = files
        self.with_annotations = with_annotations

    def resolve(self) -> []:
        for path in self.files:
            if os.path.isfile(path):
                self._check_file(path)

            if os.path.isdir(path):
                self._check_dir(path)

        return list(self.images) + list(self.annotations) + list(self.archives)

    def _check_file(self, path):
        path = resolve_path(path)
        if not os.path.exists(path):
            return

        name = os.path.basename(path)
        if is_ignored_file(name):
            return

        if not self.with_annotations and is_annotation_file(name):
            return

        if is_image_file(name):
            self.images.add(path)
            return

        if self.with_annotations and is_annotation_file(name):
            self.annotations.add(path)
            return

        if is_archive_file(name):
            self.archives.add(path)

    def _check_dir(self, path):
        for dirpath, _, filenames in os.walk(path):
            for name in filenames:
                file_path = os.path.join(dirpath, name)
                self._check_file(file_path)


def build_url(*args, **kwargs):
    url = '/'.join(map(lambda x: str(x).strip('/'), args)) + '/'
    params = []
    for key, val in kwargs.items():
        if val:
            params.append('{}={}'.format(key, val))
    if len(params):
        url += "?" + "&".join(params)

    if url.find('?') > 0 or url.find('&') > 0:
        url = url.rstrip('/')
    return url


def browse(url):
    print('Open', url)
    webbrowser.open_new_tab(url)
