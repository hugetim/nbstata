"""
Zip-safe, modern resource helpers for Python 3.10+ using importlib.resources.
Use these in place of pkg_resources.resource_filename / resource_string.
"""
from __future__ import annotations
from contextlib import contextmanager
from importlib.resources import files, as_file
from pathlib import Path
from typing import Iterator

PACKAGE = "nbstata"

def read_text(relpath: str, package: str = PACKAGE) -> str:
    """Read a packaged text resource."""
    return (files(package) / relpath).read_text()

def read_bytes(relpath: str, package: str = PACKAGE) -> bytes:
    """Read a packaged binary resource."""
    return (files(package) / relpath).read_bytes()

@contextmanager
def resource_path(relpath: str, package: str = PACKAGE) -> Iterator[Path]:
    """
    Context manager yielding a temporary real filesystem Path for a packaged
    resource. This mirrors pkg_resources.resource_filename semantics but is
    zip-safe and deprecation-proof.
    """
    with as_file(files(package) / relpath) as p:
        yield p

def resource_strpath(relpath: str, package: str = PACKAGE) -> str:
    """Return a string path for cases that strictly want str over Path."""
    with resource_path(relpath, package) as p:
        return str(p)
