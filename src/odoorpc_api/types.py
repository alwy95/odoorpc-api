from enum import Enum


class ResponseStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"


class ResponseMessage(str, Enum):
    GET = ("Data retrieved successfully",)
    POST = ("Data created successfully",)
    PUT = ("Data updated successfully",)
    PATCH = ("Data updated successfully",)
    DELETE = "Data deleted successfully"
