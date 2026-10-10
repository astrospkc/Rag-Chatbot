from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from internal.handlers import docs_handler
from internal.core import db
from internal.core.metrics import REQUEST_COUNT, CACHE_HITS, CACHE_MISSES, CACHE_LATENCY, VECTOR_SEARCH_LATENCY, LLM_LATENCY
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to DB
    print("Connecting to database...")
    try:
        app.state.db = db.get_db_connection()
        print("Database connection established.")
    except Exception as e:
        print(f"Error establishing database connection: {e}")
    
    yield
    
    # Shutdown: Close database connection
    if hasattr(app.state, "db") and app.state.db:
        app.state.db.close()
        print("Database connection closed.")


app = FastAPI(title="RAG Chatbot API", lifespan=lifespan)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust origins as needed for security in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register handler routers
app.include_router(docs_handler.router)
@app.get("/metrics")
async def metrics():
    REQUEST_COUNT.labels(user_type="system").inc()
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/")
async def root():
    return {"message": "API service is running"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
