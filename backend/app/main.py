from fastapi import FastAPI
from .database import engine, Base
from .routes import poll, vote
from fastapi import WebSocket, WebSocketDisconnect
from .websocket import manager
from .database import SessionLocal
from .models import Poll
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .core.limiter import limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi.responses import JSONResponse


from sqlalchemy.orm import joinedload

app = FastAPI()



# Create tables
Base.metadata.create_all(bind=engine)

app.include_router(poll.router)
app.include_router(vote.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*http://localhost:5173",
        "http://127.0.0.1:5173",],  # for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests, slow down."},
    )





@app.get("/")
def root():
    return {"message": "Real-Time Poll API Running 🚀"}
@app.websocket("/ws/{poll_id}")
async def websocket_endpoint(websocket: WebSocket, poll_id: str):

    await manager.connect(poll_id, websocket)

    try:
        while True:
            # Just keep connection alive
            await websocket.receive_text()

    except WebSocketDisconnect:
        manager.disconnect(poll_id, websocket)


from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded

from .database import engine, Base
from .routes import poll, vote
from .websocket import manager
from .core.limiter import limiter


app = FastAPI()

# ✅ CORS MUST COME FIRST
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Rate Limiter
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests, slow down."},
    )

# ✅ Create DB tables
Base.metadata.create_all(bind=engine)

# ✅ Include routers AFTER middleware
app.include_router(poll.router)
app.include_router(vote.router)


@app.get("/")
def root():
    return {"message": "Real-Time Poll API Running 🚀"}


@app.websocket("/ws/{poll_id}")
async def websocket_endpoint(websocket: WebSocket, poll_id: str):

    await manager.connect(poll_id, websocket)

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        manager.disconnect(poll_id, websocket)

