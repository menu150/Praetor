from fastapi import FastAPI
from .intel_feed import router as intel_router
from .skills import router as skills_router

app = FastAPI()
app.include_router(intel_router)
app.include_router(skills_router)
