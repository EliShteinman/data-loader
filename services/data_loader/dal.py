import os
import time
import mysql.connector
from contextlib import contextmanager
from typing import Optional, Dict, Any

def _env(name: str, default: Optional[str] = None) -> Optional[str]:
    val = os.getenv(name)
    return val if (val is not None and val != "") else default

def load_config() -> Dict[str, Any]:
    host = _env("DB_HOST") or _env("DATABASE_HOST") or "mysql"   # בתוך הקלאסטר: service name
    port_str = _env("DB_PORT") or "3306"

    user = (
        _env("DB_USER")
        or _env("MYSQL_DATABASE_USER")
        or _env("database-user")
    )
    password = (
        _env("DB_PASS")
        or _env("MYSQL_DATABASE_PASSWORD")
        or _env("database-password")
    )
    database = (
        _env("DB_NAME")
        or _env("MYSQL_DATABASE_NAME")
        or _env("database-name")
    )

    try:
        port = int(port_str)
    except ValueError:
        port = 3306

    cfg: Dict[str, Any] = {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "database": database,
        "connection_timeout": 5,
        "autocommit": False,
    }
    return {k: v for k, v in cfg.items() if v is not None}

_CONFIG = load_config()

@contextmanager
def get_connection(_config: Optional[Dict[str, Any]] = None, attempts: int = 3, base_delay: float = 1.0):
    cfg = _config or _CONFIG
    last_exc = None
    for attempt in range(1, attempts + 1):
        try:
            conn = mysql.connector.connect(**cfg)
            conn.ping(reconnect=False, attempts=1, delay=0)
            try:
                yield conn
            finally:
                try:
                    conn.close()
                except Exception:
                    pass
            return
        except (mysql.connector.Error, OSError) as exc:
            last_exc = exc
            if attempt < attempts:
                time.sleep(base_delay * attempt)
    raise last_exc