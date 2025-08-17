import os
from fastapi import FastAPI, HTTPException
from .data_loader import DataLoader

# Create a FastAPI app instance
app = FastAPI(
    title="Data Loader Service",
    description="A service to fetch data from a MySQL database in OpenShift.",
    version="1.0.0"
)

# --- Database Connection Setup ---
# Read database credentials from environment variables.
# This is crucial for security and flexibility in OpenShift.
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_NAME = os.getenv("DB_NAME", "mydatabase")

# Create an instance of our Data Access Layer
data_loader = DataLoader(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)

@app.on_event("startup")
def startup_event():
    """
    On application startup, attempt to connect to the database.
    """
    print("Application startup: Initializing database connection...")
    data_loader.connect()

@app.get("/data", summary="Get all data from the 'data' table")
def get_data():
    """
    This endpoint connects to the MySQL database via the DataLoader
    and returns all records from the 'data' table.
    """
    try:
        all_data = data_loader.get_all_data()
        if "error" in all_data:
             raise HTTPException(status_code=500, detail=all_data["error"])
        return all_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.get("/", summary="Health check endpoint")
def health_check():
    return {"status": "ok"}