from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
import uvicorn
from internal.handlers import docs_handler
from internal.core import db

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

# Register handler routers
app.include_router(docs_handler.router)


@app.get("/")
async def root():
    return {"message": "API service is running"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
