import os
import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv
from os.path import join, dirname
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from src.app.routers import router
from src.helpers.static_content import description, title, PUBLIC_ASSETS, FRONTEND_ROOT

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

app = FastAPI(
    title=title,
    description=description,
    version="0.1.0",
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)
app.mount("/static", StaticFiles(directory=str(FRONTEND_ROOT)), name="static")
app.mount(
    "/super-hero/public",
    StaticFiles(directory=str(PUBLIC_ASSETS)),
    name="public",
)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=str(os.getenv("HOST")),
        port=int(os.getenv("PORT")),
        reload=bool(os.getenv("DEBUG")),
        log_level="debug" if os.getenv("DEBUG") else "info",
    )
