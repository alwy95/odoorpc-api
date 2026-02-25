import importlib
from pathlib import Path


def handling_router(app):
    """
    Automatically discovers and includes FastAPI routers from the 'routes' directory.
    
    This function scans all Python files in the routes folder recursively, 
    imports them as modules, and registers any found 'router' instances 
    to the main FastAPI application.
    """
    routes_dir = Path(__file__).parent.parent / "routes"

    for route_file in routes_dir.rglob("*.py"):
        if route_file.name == "__init__.py":
            continue

        relative_path = route_file.relative_to(routes_dir)
        module_name = ".".join(relative_path.with_suffix("").parts)
        module = importlib.import_module("routes." + module_name)

        if hasattr(module, "router"):
            app.include_router(module.router)
