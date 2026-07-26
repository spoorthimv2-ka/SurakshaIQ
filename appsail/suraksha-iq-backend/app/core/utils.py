from datetime import datetime, timezone


def catalyst_datetime(dt=None):
    if dt is None:
        dt = datetime.now(timezone.utc)

    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
        except Exception:
            return dt

    return dt.strftime("%Y-%m-%d %H:%M:%S")
