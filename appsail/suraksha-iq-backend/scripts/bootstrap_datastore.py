"""Deprecated thin bridge.

Use ``app.bootstrap.datastore_bootstrap.bootstrap`` for the canonical
bootstrap implementation backed by the reusable module.
"""

from app.bootstrap.datastore_bootstrap import bootstrap as bootstrap

__all__ = ["bootstrap"]
