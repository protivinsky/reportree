from __future__ import annotations
import os
from reportree import IRTree, RTPlot
from reportree.io import IWriter, LocalWriter
from typing import Sequence, Union, Optional
import matplotlib.pyplot as plt
from yattag import Doc, indent


class Leaf(IRTree):
    """Leaf is displayed as a single HTML page. Leaf takes either matplotlib.figure.Figure or
    matplotlib.axes.Axes as input, either a single one or as a sequence. Sequence is then displayed
    over many rows of plots, with maximum row width given by num_cols.
    """

    def __init__(self, plots: Union[RTPlot, Sequence[RTPlot]], title: str = None, num_cols: int = 3):
        if not isinstance(plots, Sequence):
            plots = [plots]
        self._plots = [f if isinstance(f, plt.Figure) else f.get_figure() for f in plots]
        self._num_cols = num_cols
        if title:
            self._title = title
        else:
            if self._plots[0]._suptitle:
                self._title = self._plots[0]._suptitle.get_text()
            elif self._plots[0].axes[0].get_title():
                self._title = self._plots[0].axes[0].get_title()
            else:
                self._title = 'Leaf'

    def save(self, path: str, writer: IWriter = LocalWriter, entry: str = 'index.html'):
        n = len(self._plots)
        for i, f in enumerate(self._plots):
            writer.write_figure(os.path.join(path, f'fig_{i+1:03d}.png'), f)
        plt.close('all')

        doc, tag, text = Doc().tagtext()

        doc.asis('<!DOCTYPE html>')
        with tag('html'):
            with tag('head'):
                with tag('title'):
                    text(self._title)
            with tag('body'):
                with tag('h1'):
                    text(self._title)
                num_rows = (n + self._num_cols - 1) // self._num_cols
                for r in range(num_rows):
                    with tag('div'):
                        for c in range(min(self._num_cols, n - self._num_cols * r)):
                            doc.stag('img', src=f'fig_{self._num_cols * r + c + 1:03d}.png')

        writer.write_text(os.path.join(path, entry), indent(doc.getvalue()))





