from contextvars import ContextVar

context = ContextVar("params", default=None)
