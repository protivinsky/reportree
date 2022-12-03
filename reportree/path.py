from reportree import IRTree


class Path(IRTree):
    """(Lazily) load report from a given path. The report is copied to the destination folder only on save.

    This class is not implemented yet.
    """
    def __init__(self, path: str):
        raise NotImplementedError

    def save(self, path: str):
        raise NotImplementedError


