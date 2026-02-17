

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
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://real-time-poll-rooms-woad.vercel.app/")
# ✅ CORS MUST COME FIRST
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_URL
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

