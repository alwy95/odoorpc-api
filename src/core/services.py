from core.settings import env
from core.utils import to_dict


class OdooService:
    """
    Core service for handling Odoo XML-RPC/JSON-RPC operations.
    """

    def __init__(self, uid, password):
        """Initialize service with Odoo user ID and password credentials."""
        self.uid = uid
        self.password = password


    def _execute(self, model, method, *args, **kwargs):
        """
        Internal wrapper to execute Odoo's 'execute_kw' RPC calls. 
        It automatically injects database name and credentials into the call.
        """
        from core.jsonrpc import call

        return call(
            "object",
            "execute_kw",
            [
                env.ODOO_DB,
                self.uid,
                self.password,
                model,
                method,
                args,
                kwargs,
            ],
        )


    def create(self, model, payload):
        """Create a new record in the specified Odoo model."""
        return self._execute(model, "create", to_dict(payload))


    def write(self, model, id, payload):
        """Update an existing record identified by its Odoo ID."""
        return self._execute(model, "write", id, *to_dict(payload))


    def __getattr__(self, method_name):
        """
        Dynamically handles Odoo methods not explicitly defined (e.g., search_read).
        """
        def wrapper(model, *args, **kwargs):
            data = self._execute(model, method_name, *args, **kwargs)

            fields = kwargs.get("fields")

            if fields:
                data = (
                    [
                        {
                            f: (
                                rec[f][0]
                                if isinstance(rec[f], list) and len(rec[f]) == 2
                                else rec[f]
                            )
                            for f in fields
                        }
                        for rec in data
                    ]
                    if fields
                    else data
                )

            return data

        return wrapper
