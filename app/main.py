from fastapi import FastAPI

from app.core.database import Base, engine
from app.models import User, Customer
from app.routers.auth import router as auth_router
from app.routers.customer import router as customer_router
from app.exceptions import register_exception_handlers

app = FastAPI(
    title="Customer Management API",
    version="1.0.0"
)

register_exception_handlers(app)

app.include_router(auth_router)
app.include_router(customer_router)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {
        "message": "Customer Management API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "OK"
    }