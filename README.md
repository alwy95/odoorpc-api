# odoorpc-api

A modern FastAPI-based wrapper for Odoo RPC integration, designed to decouple integration logic from the core Odoo server and provide maximum flexibility for third-party ecosystems.

<br>

## Why odoorpc-api?
This package is intentionally built to keep your integration layer separate from the Odoo server. By decoupling these environments, you gain the freedom to integrate Odoo with various third-party platforms without affecting the core Odoo performance or stability.

<br>

## Project Roadmap 🚀
This project is currently in an **early alpha stage** and under active (but gradual) development. While the core foundation is functional, many features are still experimental. Our current roadmap includes several "work-in-progress" ideas that will be added over time:

- [ ] **Advanced Authentication:** Enhanced OAuth2 and JWT support.
- [ ] **Session Management:** Secure and persistent session handling.
- [ ] **Redis Caching:** High-performance data caching to reduce Odoo RPC overhead.
- [ ] **Third-Party Logging:** Integration with Sentry, BetterStack, or ELK.
- [ ] **CLI Scaffolding:** Generate routes, schemas, and API structures automatically with a single command.
- [ ] **AI Integration:** Seamless connection with LLMs (OpenAI, LangChain) for smart data querying.
- [ ] **And more...** to make Odoo integration smoother than ever.

<br>

## Contributing
We believe in the power of the community! If you are familiar with Odoo's internal workings or FastAPI best practices, we would love to have your contribution.

Feel free to open issues, submit PRs, or suggest new features to help this package reach its full potential.

<br>

## License
Distributed under the MIT License.

<br>

## Note
To use **Raw Query** features, you must manually install the `md_odoorpc_api` module on your Odoo server. https://github.com/alwy95/md_odoorpc_api

<br>

## Example Usage
---

### Project Setup
```bash
# Create project
mkdir -p myproject
cd myproject

# Setup virtual environment
python3.10 -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate

# Install the package
pip install odoorpc-api

# Create structure project
mkdir -p app app/routes/purchase app/routes/supplier
touch .env app/main.py

touch app/routes/purchase/__init__.py app/routes/purchase/api.py app/routes/purchase/schema.py
touch app/routes/supplier/__init__.py app/routes/supplier/api.py app/routes/supplier/schema.py
```

<br>

### Structure Project
```
myproject/                          <--- Root Project
├── .env
├── .gitignore
├── venv/
├── logs/                           <--- AUTOMATICALLY CREATED HERE LOG_FILE=True
│   └── odooapi.log
└── app/
    ├── main.py
    └── routes/
        ├── purchase/
        │   ├── __init__.py
        │   ├── api.py
        │   └── schema.py
        └── supplier/
            ├── __init__.py
            ├── api.py
            └── schema.py
```

<br>

### Configuration Management

`.env.default` (Default values)
```.env
# --- Application Settings ---
TITLE=OdooRPC API
VERSION=1.0
DEBUG=True
LOGFILE=True

# --- Server Configuration ---
HOST=127.0.0.1
PORT=9000

# --- Documentation & Swagger ---
API_URL=/docs
SAVE_SESSION_SWAGGER=False

# --- Odoo Backend Connection ---
ODOO_URL=http://127.0.0.1:8069
ODOO_DB=mydb
```

`.env` (Local overrides)
```.env
PORT=9000
HOST=127.0.0.1

ODOO_URL=http://127.0.0.1:8069
ODOO_DB=mydb
```

<br>

### Entry Point
`main.py`
```py
import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from odoorpc_api.settings import env
from odoorpc_api.exceptions import handling_exception
from odoorpc_api.routes import handling_router
from odoorpc_api.logging_config import LOGGING_CONFIG
from odoorpc_api.middleware import LoggerMiddleware


app = FastAPI(
    title=env.TITLE,
    version=env.VERSION,
    docs_url=env.API_URL, 
    swagger_ui_parameters={
        "persistAuthorization": env.SAVE_SESSION_SWAGGER,
    },
)

handling_exception(app)
handling_router(app)


app.add_middleware(LoggerMiddleware)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=env.HOST,
        port=env.PORT,
        reload=env.DEBUG,
        server_header=False,
        log_config=LOGGING_CONFIG
    )
```

### Route Implementation
`routes/purchase/api.py`
```py
from typing import Annotated
from fastapi import APIRouter, Depends, status

from odoorpc_api.jsonrpc import OdooEnv
from odoorpc_api.params import PageParams
from odoorpc_api.responses import PaginationResponse, ListResponse, SingleResponse, BaseResponse
from odoorpc_api.types import ResponseMessage

from .schema import PurchaseList, PurchaseUpdate, model, path


router = APIRouter(tags=["Purchase"])


@router.get(path, status_code=status.HTTP_200_OK, response_model=PaginationResponse[PurchaseList])
def get(q: Annotated[PageParams, Depends()], odoo = OdooEnv):
    data = odoo.search_read(
        model, 
        q.domain, 
        fields=PurchaseList.fields(), 
        limit=q.limit, 
        offset=q.offset,
    )
    total = odoo.search_count(model, q.domain)

    # PaginationResponse
    return {
        'message': ResponseMessage.GET,
        'offset': q.offset,
        'limit': q.limit,
        'total': total,
        'data': data,
    }

    # ListResponse
    # return {
    #     'message': ResponseMessage.GET,
    #     'data': data
    # }

    # SingleResponse
    # return {
    #     'message': ResponseMessage.GET,
    #     'data': data[0] if data else []
    # }

    # BaseResponse
    # return {
    #     'message': ResponseMessage.GET,
    # }


@router.post(path, status_code=status.HTTP_201_CREATED, response_model=ListResponse)
def post(payload: list[PurchaseUpdate] | PurchaseUpdate, odoo = OdooEnv):
    data = odoo.create(model, payload)
    return {
        'message': ResponseMessage.POST,
        'data': data, 
    }


@router.put(path+'/{id}', status_code=status.HTTP_200_OK, response_model=BaseResponse)
def put(id: int, payload: PurchaseUpdate, odoo = OdooEnv):
    odoo.write(model, id, payload)
    return {
        'message': ResponseMessage.PUT,
    }


@router.delete(path+'/id', status_code=status.HTTP_204_NO_CONTENT)
def delete(id: int, odoo = OdooEnv):
    odoo.button_cancel(model, id)
    odoo.unlink(model, id)
```

`routes/supplier/api.py`
```py
from typing import Annotated

from fastapi import APIRouter, Depends, status

from odoorpc_api.jsonrpc import OdooEnv
from odoorpc_api.params import PageParams
from odoorpc_api.responses import BaseResponse, PaginationResponse
from odoorpc_api.types import ResponseMessage
from odoorpc_api.utils import to_dict

from .schema import SupplierCreate, SupplierList, path


router = APIRouter(tags=["Supplier"])


@router.get(path, status_code=status.HTTP_200_OK, response_model=PaginationResponse[SupplierList])
def get(q: Annotated[PageParams, Depends()], odoo = OdooEnv):
    query = """
        select 
            count(*) over() as total_count, 
            rp.name as partner, 
            rp.type as address_type, 
            rp.function as position,
            rp.phone as phonex,
            rp.email as email, 
            rcs.name as state
        from res_partner rp
        left join res_country_state rcs on rcs.id = rp.state_id
        where rp.create_date between %(create_date_from)s and %(create_date_to)s
        and supplier_rank > 0
        limit %(limit)s offset %(offset)s
    """

    data = odoo.fetch('odoorpc.api', query, q.param_dict)
    total_data = data[0].get('total_count', 0) if data else 0
    data = [{k: v for k, v in item.items() if k != 'total_count'} for item in data]

    return {
        'message': ResponseMessage.GET,
        'offset': q.offset,
        'limit': q.limit,
        'total': total_data,
        'data': data,
    }
```

<br>

### Data Schemas
`routes/purchase/schema.py`
```py
from odoorpc_api.schemas import OdooBaseModel


path = '/purchase'
model = 'purchase.order'


class PurchaseList(OdooBaseModel):
    name: str
    partner_id: int


class PurchaseUpdate(OdooBaseModel):
    partner_id: int
```

`routes/supplier/schema.py`
```py
from odoorpc_api.schemas import OdooBaseModel

path = '/supplier'
model = 'res.partner'

class SupplierList(OdooBaseModel):
    name: str
    address_type: str
    phone: str
    position: str
    email: str
    state: str

class SupplierCreate(OdooBaseModel):
    name: str
    address_type: str
```

<br>

### Query Parameters Handling
The framework provides a default PageParams which includes 
- offset
- limit
- create_date_from (odoo field create_date)
- create_date_to (odoo field create_date)

```py
@router.get(path, status_code=status.HTTP_200_OK, response_model=PaginationResponse[PurchaseList])
def get(q: Annotated[PageParams, Depends()], odoo = OdooEnv):
```

Scenario A: Removing Parameters
If you don't need pagination or filtering, simply omit the parameter from the function:
```py
@router.get(path, status_code=status.HTTP_200_OK, response_model=PaginationResponse[PurchaseList])
def get(odoo = OdooEnv):
```

Scenario B: Custom Parameters
Create a custom Pydantic model for specific filtering requirements:

`routes/purchase/schema.py` or new file `routes/purchase/params.py`
```py
from datetime import date
from pydantic import BaseModel

class CustomPurchaseParam(BaseModel):
    number: str
    date: date
```

`routes/purchase/api.py`
```py
# from .schema import CustomPurchaseParam # from schema.py
from .params import CustomPurchaseParam

@router.get(path, status_code=status.HTTP_200_OK, response_model=PaginationResponse[PurchaseList])
def get(q: Annotated[CustomPurchaseParam, Depends()], odoo = OdooEnv):
```
<br>

### Execution
```bash
python main.py

# Open: http://127.0.0.1/9000/docs
```