import json
import logging
import os
import time
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from flask import has_request_context, request, session


_request_id = ContextVar("o3_request_id", default=None)
_configured = False


class JsonFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "timestamp": datetime.fromtimestamp(record.created, timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "process": record.process,
        }
        request_id = _request_id.get()
        if request_id:
            payload["request_id"] = request_id
        if has_request_context():
            payload["method"] = request.method
            payload["path"] = request.path
            payload["remote_addr"] = request.remote_addr
            payload["user_agent"] = (request.headers.get("User-Agent") or "")[:255]
            if session.get("usuario_id"):
                payload["usuario_id"] = session.get("usuario_id")
        for key in ("operation", "service", "repository", "status_code", "duration_ms", "exception_type"):
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=True, default=str)


def get_logger(category):
    return logging.getLogger(f"o3cloud.{category}")


def set_request_id(value=None):
    return _request_id.set(value or str(uuid.uuid4()))


def clear_request_id(token):
    _request_id.reset(token)


def configure_logging():
    global _configured
    if _configured:
        return
    log_dir = Path(os.getenv("O3_LOG_DIR", "/opt/o3cloud-manager/logs"))
    log_dir.mkdir(parents=True, exist_ok=True)
    formatter = JsonFormatter()
    files = {
        "access": ("access.log", logging.INFO),
        "application": ("application.log", logging.INFO),
        "error": ("error.log", logging.ERROR),
        "database": ("database.log", logging.ERROR),
        "integrations": ("integrations.log", logging.INFO),
        "security": ("security.log", logging.INFO),
        "jobs": ("jobs.log", logging.INFO),
    }
    for category, (filename, level) in files.items():
        logger = get_logger(category)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
        if logger.handlers:
            continue
        handler = TimedRotatingFileHandler(
            log_dir / filename,
            when="midnight",
            interval=1,
            backupCount=int(os.getenv("O3_LOG_BACKUP_COUNT", "30")),
            encoding="utf-8",
            utc=True,
        )
        handler.setLevel(level)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        os.chmod(handler.baseFilename, 0o640)
    get_logger("application").info("Backend logging initialized", extra={"operation": "STARTUP"})
    _configured = True


def init_request_logging(app):
    configure_logging()
    access_logger = get_logger("access")
    error_logger = get_logger("error")

    @app.before_request
    def start_request_logging():
        token = set_request_id(request.headers.get("X-Request-ID"))
        request.environ["o3_request_id_token"] = token
        request.environ["o3_request_started_at"] = time.perf_counter()

    @app.after_request
    def finish_request_logging(response):
        started = request.environ.get("o3_request_started_at")
        duration_ms = round((time.perf_counter() - started) * 1000, 2) if started else None
        access_logger.info(
            "HTTP request completed",
            extra={"status_code": response.status_code, "duration_ms": duration_ms},
        )
        response.headers["X-Request-ID"] = _request_id.get() or ""
        return response

    @app.teardown_request
    def log_request_exception(error):
        if error is not None:
            error_logger.error("Unhandled Flask request exception", exc_info=(type(error), error, error.__traceback__))
        token = request.environ.get("o3_request_id_token")
        if token is not None:
            clear_request_id(token)
