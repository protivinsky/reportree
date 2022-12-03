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

    """

    def __init__(self, children: Union[IRTree, RTPlot, Sequence[Union[IRTree, RTPlot]]], title: Optional[str] = None):
        if not isinstance(children, Sequence):
            children = [children]
        self._children = [ch if isinstance(ch, IRTree) else Leaf(ch) for ch in children]
        self._title = title or 'Branch'

    def save(self, path: str, writer: IWriter = LocalWriter, entry: str = 'index.html'):
        ch_titles = [ch._title for ch in self._children]
        if len(set(ch_titles)) < len(ch_titles):
            ch_titles = [f'{t}_{i:02d}' for i, t in enumerate(ch_titles)]
        for t, ch in zip(ch_titles, self._children):
            ch.save(os.path.join(path, slugify(t)), writer=writer, entry=entry)

        doc, tag, text, line = Doc().ttl()

        doc.asis('<!DOCTYPE html>')
        with tag('html'):
            with tag('head'):
                with tag('title'):
                    text(self._title)
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
                with tag('h1'):
                    text(self._title)
                with tag('div'):
                    for t in ch_titles:
                        line('button', t, type='button', onclick='loader(\'content\', \'{}\')'.format(slugify(t)))
                with tag('div', id='content'):
                    text('')
                with tag('script'):
                    doc.asis('loader(\'content\', \'{}\')'.format(slugify(ch_titles[0])))

        writer.write_text(os.path.join(path, entry), indent(doc.getvalue()))
