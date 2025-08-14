from contextlib import asynccontextmanager
from fastapi import FastAPI
from services.data_loader.ops import create_table, insert_data, get_all_data

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_table()
    insert_data()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/get_data")
def get_data():
    return get_all_data()

@app.get("/healthz")
def healthz():
    return {"ok": True}