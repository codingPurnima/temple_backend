from fastapi import FastAPI
from app.db.database import engine, Base
from app.models import user, character, event, lyrics, notification, event_registration, roles, app_content, dashboard_image
from app.api.routes import admin, admin_content, auth, content, event, notification, dashboard, character, lyrics
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "API running"}

app.include_router(auth.router, prefix="/auth")
app.include_router(event.router, prefix="/events")
app.include_router(notification.router, prefix="/notifications")
app.include_router(dashboard.router, prefix="/dashboard")
app.include_router(character.router, prefix="/characters")
app.include_router(lyrics.router, prefix="/lyrics")
app.include_router(admin.router, prefix="/admin")
app.include_router(content.router, prefix= "/content")
app.include_router(admin_content.router, prefix="/admin-content")