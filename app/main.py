from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.api import router

# Initialize FastAPI app
app = FastAPI(
    title="Elysian Insurance Services - Claim Conductor Phonebook Integration",
    description="Service that handles incoming webhook notifications from a phonebook, manages internal state, and allows querying for current user names.",
    version="1.0.0",
)

# Include API router
app.include_router(router)

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/nl-to-sql", response_class=HTMLResponse)
async def serve_nl_to_sql():
    with open("nl_to_sql.html") as f:
        return HTMLResponse(f.read())  # checking push from GH
