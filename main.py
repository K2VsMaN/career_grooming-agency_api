from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def get_home():
    return {
        "status": "ok",
        "message": "Welcome to Career Grooming Agency"
    }