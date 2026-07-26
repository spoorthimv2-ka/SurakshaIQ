import json
import logging
import sys
import traceback

from pathlib import Path

log = logging.getLogger("system_setup")

log.info("[BOOTSTRAP] system_setup handler starting")

try:
    from catalyst_bootstrap.datastore_bootstrap import bootstrap as _bootstrap
    log.info("[BOOTSTRAP] Successfully imported catalyst_bootstrap.datastore_bootstrap")
except ImportError as _import_err:
    tb = traceback.format_exc()
    log.error("[BOOTSTRAP] Failed to import bootstrap module: %s\n%s", _import_err, tb)
    raise ImportError(
        f"Failed to import bootstrap module from local catalyst_bootstrap package. Error: {_import_err}"
    )


def handler(context, basicio):
    log.info("[BOOTSTRAP] handler() invoked, context type=%s", type(context).__name__)
    try:
        log.info("[BOOTSTRAP] About to call bootstrap()")
        result = _bootstrap()
        log.info(
            "[BOOTSTRAP] bootstrap() returned: success=%s, tables_created=%s, rows_inserted=%s",
            result.get("success"),
            result.get("tables_created"),
            result.get("rows_inserted"),
        )
        basicio.write(json.dumps(result))
        log.info("Bootstrap completed successfully")
    except Exception as exc:
        tb = traceback.format_exc()
        log.error("[BOOTSTRAP] Bootstrap failed: %s\n%s", exc, tb)
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

