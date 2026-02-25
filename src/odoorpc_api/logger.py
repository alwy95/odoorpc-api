import logging.config
import time
from urllib.parse import unquote_plus

from uvicorn.config import LOGGING_CONFIG

from odoorpc_api.context import context

logging.config.dictConfig(LOGGING_CONFIG)

odooapi_logger = logging.getLogger("odooapi_logger")
logger = logging.getLogger(__name__)


class OdooAPILogger:
    """
    Custom logger handler for Odoo RPC request/response activities.
    """

    def __init__(self):
        """Initialize logger levels mapping to standard logging functions."""
        self.LEVELS = {
            "info": odooapi_logger.info,
            "error": odooapi_logger.error,
        }


    def info(self, msg=None):
        """Log a message with INFO severity."""
        self._process(type="info", msg=msg)


    def error(self, msg, code=None):
        """Log a message with ERROR severity and optional HTTP status code."""
        self._process(type="error", msg=msg, code=code)


    def _process(self, type=None, msg=None, code=None):
        """
        Main processing logic for extracting metadata and formatting the log content.
        
        Fetches request, response, and timing data from the global async context.
        """
        ctx = context.get() or {}

        req = ctx.get("req")
        res = ctx.get("res")
        start = ctx.get("start")

        if not req or start is None:
            log_func = self.LEVELS.get(type, odooapi_logger.info)
            log_func(f"[SYSTEM] {msg}" if msg else "[SYSTEM] No request context")
            return
        
        response_time = self._get_response_time(time.time() - start)

        status_code = getattr(res, "status_code", code)
        method = req.method
        path = req.scope.get("path", "/")
        params = unquote_plus(str(req.query_params))

        host_port = f"{req.client.host}:{req.client.port}"

        http = (
            f"{req.scope.get('type', 'HTTP').upper()}/"
            f"{req.scope.get('http_version', '1.1')}"
        )

        uid = "no uid"
        content_length = "0Bytes"

        if res:
            uid = res.headers.get("uid", uid)
            content_length = self._get_content_length(
                res.headers.get("content-length", 0)
            )

            if "uid" in res.headers:
                del res.headers["uid"]

        messages = [
            host_port,
            method,
            status_code,
            path,
            http,
            uid,
            content_length,
            response_time,
        ]

        if params:
            messages.insert(5, params)
        if msg:
            messages.append(msg)

        log_content = " - ".join([str(m) for m in messages])
        
        log_func = self.LEVELS.get(type, odooapi_logger.info)
        log_func(log_content)


    def _get_response_time(self, t):
        """Convert duration in seconds to a human-readable string format."""
        if t < 1:
            return f"{t * 1000:.1f}ms"
        if t < 60:
            return f"{t:.1f}s"
        return f"{t / 60:.1f}m"


    def _get_content_length(self, length):
        """Convert payload size in bytes to a human-readable size unit."""
        try:
            length = int(length)
            if length < 1024:
                return f"{length}Bytes"
            if length < 1024 * 1024:
                return f"{length / 1024:.1f}KB"
            return f"{length / (1024 * 1024):.1f}MB"
        except Exception:
            return "0Bytes"


# Expose the logger instance as a global object 'log'
log = OdooAPILogger()