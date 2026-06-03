from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth as auth_router
from app.routers import users as users_router
from app.routers import posts as posts_router
from app.routers import clubs as clubs_router
from app.routers import events as events_router

app = FastAPI(title="CampusHub API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router, prefix="/api/auth", tags=["auth"])
app.include_router(users_router.router, prefix="/api/users", tags=["users"])
app.include_router(posts_router.router, prefix="/api/posts", tags=["posts"])
app.include_router(clubs_router.router, prefix="/api/clubs", tags=["clubs"])
app.include_router(events_router.router, prefix="/api/events", tags=["events"])


@app.get("/")
def root():
    return {"message": "CampusHub API Running", "status": "ok"}