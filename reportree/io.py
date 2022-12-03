import os
from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
import re
import unicodedata


def slugify(value, allow_unicode=False):
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces to hyphens.
    Remove characters that aren't alphanumerics, underscores, or hyphens.
    Convert to lowercase. Also strip leading and trailing whitespace.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return re.sub(r'[-\s]+', '-', value)


class IWriter(ABC):

    @staticmethod
    @abstractmethod
    def write_text(path: str, text: str):
        ...

    @staticmethod
    @abstractmethod
    def write_figure(path: str, figure: plt.Figure):
        ...


class LocalWriter(IWriter):

    @staticmethod
    def write_text(path: str, text: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)

    @staticmethod
    def write_figure(path: str, figure: plt.Figure):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        figure.savefig(path)

