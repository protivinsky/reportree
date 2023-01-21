import os
import re
import shutil
from typing import Optional
from reportree import IRTree


class Path(IRTree):
    """(Lazily) load report from a given path. The report is copied to the destination folder only on save.
    Support for Writer (to allow other file systems such as AWS or GCP) is not implemented yet.
    """
    def __init__(self, path: str, entry: Optional[str] = None, title: Optional[str] = None):
        entry = entry or 'index.htm'
        if os.path.isfile(path):
            entry = os.path.basename(path)
            path = os.path.dirname(path)
        self._path = path
        self._entry = entry
        if title is None:
            with open(os.path.join(self._path, self._entry), 'r', encoding='utf-8') as f:
                title_search = re.search('<title>(.*)</title>', f.read())
            if title_search:
                title = title_search.group(1)
            else:
                title = 'ReportTree Path'
        self._title = title

    def save(self, path: str, writer=None, entry: str = 'index.htm'):
        # Support for custom writers is not implemented yet. It is not clear how such cases should be handled.
        # However, Branch passes the writer down, so we cannot throw a NotImplementedError here.
        os.makedirs(path, exist_ok=True)
        for x in os.listdir(self._path):
            x = os.path.join(self._path, x)
            # rename entry point
            if os.path.normpath(x) == os.path.normpath(os.path.join(self._path, self._entry)):
                shutil.copy2(x, os.path.join(path, entry))
            else:
                if os.path.isfile(x):
                    shutil.copy2(x, path)
                elif os.path.isdir(x):
                    shutil.copytree(x, path)
