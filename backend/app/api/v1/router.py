from fastapi import APIRouter

from .endpoints import admin, auth, bookings, checkin, eligibility, incidents, notifications, resources, users

api_router = APIRouter()
for mod, prefix in [
    (auth, "/auth"), (users, "/users"), (resources, "/resources"), (bookings, "/bookings"), (eligibility, "/eligibility"),
    (checkin, "/handover"), (incidents, "/incidents"), (notifications, "/notifications"), (admin, "/admin"),
]:
    api_router.include_router(mod.router, prefix=prefix, tags=[prefix.strip("/")])
