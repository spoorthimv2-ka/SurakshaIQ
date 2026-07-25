import json
import logging
import sys
from pathlib import Path

log = logging.getLogger("system_setup")

# [TEMP LOGGING] Module entry point
log.info("[TEMP] system_setup module loaded")
# [END TEMP LOGGING]

try:
    from catalyst_bootstrap.datastore_bootstrap import bootstrap as _bootstrap
    log.info("[TEMP] Successfully imported catalyst_bootstrap.datastore_bootstrap")
except ImportError as _import_err:
    log.error("[TEMP] Failed to import bootstrap module: %s", _import_err)
    raise ImportError(
        f"Failed to import bootstrap module from local catalyst_bootstrap package. Error: {_import_err}"
    )


def handler(context, basicio):
    log.info("[TEMP] handler() invoked")
    try:
        log.info("[TEMP] About to call bootstrap()")
        result = _bootstrap()
        log.info(
            "[TEMP] bootstrap() returned: success=%s, tables_created=%s, rows_inserted=%s",
            result.get("success"),
            result.get("tables_created"),
            result.get("rows_inserted"),
        )
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
