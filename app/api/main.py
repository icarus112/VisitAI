from fastapi import FastAPI
from app.api.endpoints.payments import router as payment_router

app = FastAPI(title="VisitAI")
app.include_router(payment_router)