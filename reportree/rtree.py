from abc import ABC, abstractmethod
from typing import Union
import matplotlib.pyplot as plt
from reportree.io import IWriter, LocalWriter


RTPlot = Union[plt.Figure, plt.Axes]


class IRTree(ABC):

    @abstractmethod
    def save(self, path: str, writer: IWriter = LocalWriter, entry: str = 'index.html'):
        ...
