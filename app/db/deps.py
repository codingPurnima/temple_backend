from .database import SessionLocal #relative import; without the dot, it would be absolute

def get_db():
    db= SessionLocal()
    try:
        yield db
    finally:
        db.close()