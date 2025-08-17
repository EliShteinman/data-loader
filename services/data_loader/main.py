import os
from fastapi import FastAPI, HTTPException
from .data_loader import DataLoader
from contextlib import asynccontextmanager

# שלב 1: קריאת הגדרות החיבור למסד הנתונים ממשתני סביבה.
# בפריסה ל-OpenShift, המשתנים האלה מוזרקים על ידי קובץ ה-Deployment.
# לפיתוח מקומי, ניתן להגדיר ערכי ברירת מחדל (למשל, "localhost").
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_NAME = os.getenv("DB_NAME", "mydatabase")

# שלב 2: יצירת מופע יחיד של ה-DataLoader.
# זהו האובייקט שינהל עבורנו את כל התקשורת עם מסד הנתונים.
data_loader = DataLoader(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)

# שלב 3: הגדרת לוגיקה שתרוץ פעם אחת בעת עליית השרת.
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    בעת עליית האפליקציה, ננסה להתחבר למסד הנתונים.
    """
    print("Application startup: Initializing database connection...")
    data_loader.connect() # קריאה לפונקציית החיבור
    yield
    # כאן ניתן להוסיף קוד שירוץ בכיבוי השרת, למשל סגירת חיבורים.


# שלב 4: יצירת אפליקציית FastAPI והגדרת ה-lifespan.
app = FastAPI(
    title="Data Loader Service",
    description="A service to fetch data from a MySQL database in OpenShift.",
    version="1.0.0",
    lifespan=lifespan
)


# שלב 5: יצירת נקודת קצה (endpoint) ראשית.
@app.get("/data", summary="Get all data from the 'data' table")
def get_data():
    """
    נקודת קצה זו משתמשת ב-DataLoader כדי למשוך
    את כל הרשומות מטבלת 'data' ולהחזיר אותן.
    """
    try:
        # קריאה לפונקציה בשכבת הנתונים שמביאה את המידע.
        all_data = data_loader.get_all_data()
        if "error" in all_data:
             # אם שכבת הנתונים החזירה שגיאה, נחזיר אותה למשתמש עם קוד 500.
             raise HTTPException(status_code=500, detail=all_data["error"])
        return all_data
    except Exception as e:
        # טיפול בשגיאות לא צפויות.
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.get("/", summary="Health check endpoint")
def health_check():
    return {"status": "ok"}