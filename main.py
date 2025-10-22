from fastapi import FastAPI

from api.routes.health import health_router

app = FastAPI(title="Car Insurance API", version="0.1.0")

# Routers
app.include_router(health_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)