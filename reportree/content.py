import os
from typing import Union
from yattag import Doc, indent
from .rtree import IRTree
from .io import IWriter, LocalWriter


class Content(IRTree):
    """Content is a leaf node that contains an arbitrary HTML code.
    """

    def __init__(self, content: Union[str, Doc], title: str = None, body_only: bool = True):
        """Content is a leaf node that contains an arbitrary HTML code.

        Args:
            content: Arbitrary HTML code, either as a string or as yattag's Doc instance.
            title: Title of the produced HTML page (used only if `body_only` is True).
            body_only: If True, then the content is wrapped within `body` tag.
        """
        self._content = content if isinstance(content, str) else indent(content.getvalue())
        self._title = title or 'Content'
        self._body_only = body_only

    def save(self, path: str, writer: IWriter = LocalWriter, entry: str = 'index.html'):
        if self._body_only:
            doc, tag, text, line = Doc().ttl()
            doc.asis('<!DOCTYPE html>')
            with tag('html'):
                with tag('head'):
                    doc.stag('meta', charset='UTF-8')
                    line('title', self._title)
                with tag('body'):
                    doc.asis(self._content)
            content = indent(doc.getvalue())
        else:
            content = self._content
        writer.write_text(os.path.join(path, entry), content)
