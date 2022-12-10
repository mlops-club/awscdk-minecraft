from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

# pip install uvicorn

# FastAPI: https://fastapi.tiangolo.com/tutorial/first-steps/
# Rootski API docs: https://api.rootski.io/docs
