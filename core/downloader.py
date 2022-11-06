from contextlib import contextmanager


@contextmanager
def already_downloaded(fp: str, _):
    yield fp
