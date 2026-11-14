from fastapi import APIRouter
from api.endpoints import merch, auth, employees, transactions, reports

api_router = APIRouter()

api_router.include_router(merch.router, prefix="/merch", tags=["merch"])
api_router.include_router(auth.router, tags=["auth"])          # prefix внутри router
api_router.include_router(employees.router, tags=["employees"])
api_router.include_router(transactions.router, tags=["transactions"])
api_router.include_router(reports.router, tags=["reports"])