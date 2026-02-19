from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.database import Base, engine

import app.models  

from app.routes import auth_routes, user_routes, attendance_routes, setup_routes




app = FastAPI(
    title="HRMS Lite API",
    description="Backend API for HRMS Lite Application",
    version="1.0.0"
)




Base.metadata.create_all(bind=engine)




app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://hrms-frontend-i74w.onrender.com"  
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Validation Error",
            "errors": exc.errors(),
        },
    )


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Database Error",
            "details": str(exc),
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal Server Error",
            "details": str(exc),
        },
    )



@app.get("/", tags=["Health"])
def root():
    return {
        "success": True,
        "message": "HRMS Backend Running 🚀"
    }


app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(attendance_routes.router)
app.include_router(setup_routes.router)



