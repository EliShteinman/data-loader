import os
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager

# Import the shared components: the data access layer and the API routers
from .data_loader import DataLoader
from .routers import items

# --- Step 1: Configuration ---
# Read database connection settings from environment variables.
# These are injected by the OpenShift Deployment manifest.
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_NAME = os.getenv("DB_NAME", "mydatabase")

# --- Step 2: Singleton Instance Creation ---
# Create a single, shared instance of the DataLoader.
# This object will be used by all API endpoints to interact with the database.
data_loader = DataLoader(
    host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME
)


# --- Step 3: Lifespan Management ---
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


# --- Step 4: FastAPI App Instantiation ---
# Create the main FastAPI application instance.
app = FastAPI(
    title="Data Loader Service",
    description="A service to fetch and manage data in a MySQL database on OpenShift.",
    version="2.0.0",  # Version updated to reflect new CRUD functionality
    lifespan=lifespan,
)

# --- Step 5: Include Routers ---
# Mount the CRUD API router into the main application.
# All endpoints from `items.py` will be included under the `/items` prefix.
app.include_router(items.router)

# --- Step 6: Define Core/Legacy Endpoints ---
# These endpoints are defined directly on the main 'app' object.


@app.get(
    "/data",
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
