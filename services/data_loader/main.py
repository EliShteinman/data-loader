import os
from fastapi import FastAPI, HTTPException
from .data_loader import DataLoader
from contextlib import asynccontextmanager

# שלב 1: קריאת הגדרות החיבור
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_NAME = os.getenv("DB_NAME", "mydatabase")

# שלב 2: יצירת מופע יחיד של ה-DataLoader
data_loader = DataLoader(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)

# שלב 3: הגדרת לוגיקה לעלייה וכיבוי השרת
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup: Initializing database connection...")
    data_loader.connect()
    yield
    # ADDED: קריאה לסגירת החיבור בסיום חיי האפליקציה
    print("Application shutdown: Closing database connection...")
    data_loader.close()

# שלב 4: יצירת אפליקציית FastAPI
app = FastAPI(
    title="Data Loader Service",
    description="A service to fetch data from a MySQL database in OpenShift.",
    version="1.0.0",
    lifespan=lifespan
)

# שלב 5: יצירת נקודות קצה (endpoints)
@app.get("/data", summary="Get all data from the 'data' table")
def get_data():
    try:
        all_data = data_loader.get_all_data()
        # IMPROVED: בדיקה חזקה יותר לשגיאות
        if isinstance(all_data, dict) and "error" in all_data:
             raise HTTPException(status_code=500, detail=all_data["error"])
        return all_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.get("/", summary="Health check endpoint")
def health_check():
    return {"status": "ok"}