from fastapi import FastAPI
# from app.metrics.routes import router as metric_router
from app.metrics.routes import router as metrics_router

app = FastAPI()

# include the router this is similar to including app/urls.py to project/urls.py
app.include_router(metrics_router)
