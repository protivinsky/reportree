import os
from reportree import IRTree, RTPlot, Leaf
from reportree.io import IWriter, LocalWriter, slugify
from typing import Sequence, Union, Optional
from yattag import Doc, indent


class Branch(IRTree):
    """Branch produces a navigation bar with buttons for selecting between its children.

    .. warning::
        The selection of pages in nested reports works correctly only when served from the webserver (even the Python one
        works fine for local development, `python -m http.server`).

        The selection is done via Javascript and the targets are loaded on the fly. When the reports are
        displayed locally, different files are considered as Cross-Origin access and the loading is blocked
        by the browser. Single page reports (i.e. Leaves) work fine.

        This issue can be solved by using Mozilla Firefox for local browsing with changing
        `security.fileuri.strict_origin_policy` to `false` (in `about:config`).

    Args:
        children: List of children nodes.
        title: Title of the produced HTML page.
        labels: Button labels to access children pages. If not provided, children's titles are used as labels.
    """

    def __init__(self,
                 children: Union[IRTree, RTPlot, Sequence[Union[IRTree, RTPlot]]],
                 title: Optional[str] = None,
                 labels: Optional[Union[str, Sequence[str]]] = None):
        if not isinstance(children, Sequence):
            children = [children]
        self._children = [ch if isinstance(ch, IRTree) else Leaf(ch) for ch in children]
        self._title = title or 'Branch'
        if labels is None:
            labels = [ch._title for ch in self._children]
            if len(set(labels)) < len(labels):
                labels = [f'{t}_{i:02d}' for i, t in enumerate(labels)]
        else:
            if not isinstance(labels, Sequence):
                labels = [labels]
            if len(self._children) != len(labels):
                raise TypeError('Labels have to have the same length as children.')
            if len(set(labels)) < len(labels):
                raise ValueError('Provided labels have to be unique.')
        self._labels = labels

    def save(self, path: str, writer: IWriter = LocalWriter, entry: str = 'index.html'):
        for lbl, ch in zip(self._labels, self._children):
            ch.save(os.path.join(path, slugify(lbl)), writer=writer, entry=entry)

        doc, tag, text, line = Doc().ttl()

        doc.asis('<!DOCTYPE html>')
        with tag('html'):
            with tag('head'):
                doc.stag('meta', charset='UTF-8')
                line('title', self._title)
                with tag('script'):
                    doc.asis("""
                      function loader(target, file) {
                        var element = document.getElementById(target);
                        var xmlhttp = new XMLHttpRequest();
                        xmlhttp.onreadystatechange = function(){
                          if(xmlhttp.status == 200 && xmlhttp.readyState == 4){          
                            var txt = xmlhttp.responseText;
                            var next_file = ""
                            var matches = txt.match(/<script>loader\\('.*', '(.*)'\\)<\\/script>/);
                            if (matches) {
                              next_file = matches[1];
                            };            
                            txt = txt.replace(/^[\s\S]*<body>/, "").replace(/<\/body>[\s\S]*$/, "");
                            txt = txt.replace(/src=\\"fig_/g, "src=\\"" + file + "/fig_");
                            txt = txt.replace(/loader\\('/g, "loader('" + file.replace("/", "-") + "-");
                            txt = txt.replace(/div id=\\"/, "div id=\\"" + file.replace("/", "-") + "-");
                            txt = txt.replace(/content', '/g, "content', '" + file + "/");
                            element.innerHTML = txt;
                            if (next_file) {
                              loader(file.replace("/", "-") + "-content", file + "/" + next_file);
                            };            
                          };
                        };
                        xmlhttp.open("GET", file + """ + f'"/{entry}"' + """, true);
                        xmlhttp.send();
                      }
                    """)
            with tag('body'):
                line('h1', self._title)
                with tag('div'):
                    for lbl in self._labels:
                        line('button', lbl, type='button', onclick='loader(\'content\', \'{}\')'.format(slugify(lbl)))
                line('div', '', id='content')
                with tag('script'):
                    doc.asis('loader(\'content\', \'{}\')'.format(slugify(self._labels[0])))

        writer.write_text(os.path.join(path, entry), indent(doc.getvalue()))
