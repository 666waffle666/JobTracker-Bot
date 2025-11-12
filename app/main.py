from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()


@app.get("/")
async def get_root():
    return JSONResponse(content={"message": "Hello!"})
