from dotenv import load_dotenv
load_dotenv()



from fastapi import FastAPI

from app.api.search import router as search_router

app = FastAPI(
    title="Document Search Service"
)

app.include_router(
    search_router,
    prefix="/api",
    tags=["Search"]
)
