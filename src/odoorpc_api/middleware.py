import time

from starlette.middleware.base import BaseHTTPMiddleware

from odoorpc_api.context import context
from odoorpc_api.logger import log


class LoggerMiddleware(BaseHTTPMiddleware):
    """
    Middleware to intercept HTTP requests and responses for centralized logging.
    """
    async def dispatch(self, req, call_next: BaseHTTPMiddleware):
        """
        Processes each request, capturing metadata and handling exceptions 
        to ensure all transactions are logged and context is safely reset.
        """
        token = context.set({"req": req, "start": time.time()})
        try:
            res = await call_next(req)

            ctx = context.get()
            ctx["res"] = res
            context.set(ctx)

            if res.status_code < 400:
                log.info()

            return res

        except Exception as e:
            token = context.set({"req": req, "start": time.time()})
            raise e

        finally:
            context.reset(token)
