import json
import random
from typing import Annotated

import requests
from fastapi import Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPBasic

from odoorpc_api.services import OdooService
from odoorpc_api.settings import env

security = HTTPBasic()


def call(service, method, args):
    """Execute JSON-RPC 2.0 calls to Odoo and handle server-side exceptions."""
    try:
        data = {
            "jsonrpc": 2.0,
            "method": "call",
            "params": {"service": service, "method": method, "args": args},
            "id": random.randint(0, 1000000),
        }

        url = f"{env.ODOO_URL}/jsonrpc"

        res = requests.post(
            url,
            data=json.dumps(data).encode(),
            headers={
                "Content-Type": "application/json",
            },
        )

        res.raise_for_status()

        data = res.json()
        result = data.get("result")

        # set global error from odoo exception
        if data.get("error"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=data["error"]["data"]["message"],
            )

        if isinstance(result, dict) and result.get("error"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=result.get("error")
            )

        return result

    except requests.exceptions.RequestException as e:
        status_code = (
            e.response.status_code
            if e.response
            else status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        raise HTTPException(status_code=status_code, detail=str(e))


def authenticate(
    credentials: Annotated[HTTPBasic, Depends(security)],
    request: Request,
    response: Response,
):
    """FastAPI dependency to authenticate Odoo credentials and initialize OdooService."""
    uid = call(
        "common", "login", [env.ODOO_DB, credentials.username, credentials.password]
    )
    response.headers["uid"] = str(uid)

    service = OdooService(uid, credentials.password)
    service.request = request

    return service


# Shortcut for using the authenticated service in route handlers
OdooEnv = Depends(authenticate)