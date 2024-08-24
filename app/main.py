from fastapi import FastAPI
from app.api import v1_router
from app.db import db

app = FastAPI()
app.include_router(v1_router)

@app.on_event("shutdown")
def close_db():
    return db.close()
