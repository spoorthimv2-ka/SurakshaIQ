"""Deprecated thin bridge.

Use ``catalyst_bootstrap.datastore_bootstrap.bootstrap`` for the canonical
bootstrap implementation backed by the reusable module.
"""

import sys
from pathlib import Path

_repo_root = Path(__file__).resolve().parents[3]
_system_setup_dir = _repo_root / "functions" / "system_setup"
if str(_system_setup_dir) not in sys.path:
    sys.path.insert(0, str(_system_setup_dir))

from catalyst_bootstrap.datastore_bootstrap import bootstrap as bootstrap

__all__ = ["bootstrap"]
