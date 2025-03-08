from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, user, bookings, events, seats, seats_in_events, venues
from fastapi.openapi.utils import get_openapi

# Create all tables (in production, use Alembic for migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(root_path="/api",
    title="FastAPI",
    description="Sluvik's API"
)

# Define allowed origins (adjust the list to your requirements)
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://vyachik.ru",
    "http://www.vyachik.ru",
]

# Add CORS middleware to the FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of origins allowed to make requests
    allow_credentials=True,
    allow_methods=["*"],    # Allows all HTTP methods (GET, POST, PUT, etc.)
    allow_headers=["*"],    # Allows all headers
)

# Include your API routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(user.router, prefix="/users", tags=["users"])
app.include_router(bookings.router, prefix="/bookings", tags=["bookings"])
app.include_router(events.router, prefix="/events", tags=["events"])
app.include_router(seats.router, prefix="/seats", tags=["seats"])
app.include_router(seats_in_events.router, prefix="/seats_in_events", tags=["seats_in_events"])
app.include_router(venues.router, prefix="/venues", tags=["venues"])
