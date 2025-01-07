from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {
        "status_code": 200,
        "message": "Welcome to the API",
        "data": {
            "version": "1.0.0",
            "documentation": "/docs"
        }
    }
