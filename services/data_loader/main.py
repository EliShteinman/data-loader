from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from typing import List

# Import the shared components: the data access layer, API routers, and models
from .core.dependencies import data_loader
from .crud import items
from . import models


# --- Lifespan Management ---
# Define logic that runs once on application startup and once on shutdown.
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    On application startup, initialize the database connection pool.
    On shutdown, resources will be released.
    """
    print("Application startup: Initializing database connection pool...")
    data_loader.connect()
    yield
    print("Application shutdown: Releasing database connection resources...")
    data_loader.close()


# --- FastAPI App Instantiation ---
# Create the main FastAPI application instance.
app = FastAPI(
    title="Data Loader Service",
    description="A service to fetch and manage data in a MySQL database on OpenShift.",
    version="2.0.0",  # Version updated to reflect new CRUD functionality
    lifespan=lifespan,
)

# --- Include Routers ---
# Mount the CRUD API router into the main application.
# All endpoints from `items.py` will be included under the `/items` prefix.
app.include_router(items.router)

# --- Define Core/Legacy Endpoints ---
# These endpoints are defined directly on the main 'app' object.


@app.get(
    "/data",
    # ★★★ הוספת ה-response_model ★★★
    response_model=List[models.Item],
    summary="Get all data (Legacy)",
    description="The original endpoint to fetch all records from the 'data' table.",
    tags=["Legacy"],
)
def get_all_data_legacy():
    """
    This is the original endpoint required by the project.
    For a more conventional REST API, use GET /items/ instead.
    """
    try:
        all_data = data_loader.get_all_data()
        if isinstance(all_data, dict) and "error" in all_data:
            raise HTTPException(status_code=500, detail=all_data["error"])
        return all_data
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )


@app.get(
    "/",
    summary="Health Check",
    description="A simple health check endpoint to verify the service is running.",
    tags=["Monitoring"],
)
def health_check():
    """
    Returns a 200 OK with a status message.
    This is used by Kubernetes/OpenShift liveness and readiness probes.
    """
    return {"status": "ok"}