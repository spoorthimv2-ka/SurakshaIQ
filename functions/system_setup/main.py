import json
import logging
import os
import sys
from pathlib import Path

log = logging.getLogger("system_setup")

_this_file = Path(__file__).resolve()
_project_root = _this_file.parents[2]
_appsail_dir = _project_root / "appsail" / "suraksha-iq-backend"
_path_candidates = [
    str(_appsail_dir),
    str(_project_root),
]
for _p in _path_candidates:
    if _p not in sys.path:
        sys.path.insert(0, _p)

try:
    from app.bootstrap.datastore_bootstrap import bootstrap as _bootstrap
except ImportError as _import_err:
    raise ImportError(
        f"Failed to import bootstrap module. Tried paths: {_path_candidates}. Error: {_import_err}"
    )


def handler(context, basicio):
    try:
        result = _bootstrap()
        basicio.write(json.dumps(result))
        log.info("Bootstrap completed successfully")
    except Exception as exc:
        log.exception("Bootstrap failed")
        basicio.write(
            json.dumps(
                {
                    "success": False,
                    "sdk_capabilities": {},
                    "tables_created": 0,
                    "tables_existing": 0,
                    "rows_inserted": 0,
                    "duplicates_skipped": 0,
                    "errors": [str(exc)],
                }
            )
        )
    finally:
        context.close()
