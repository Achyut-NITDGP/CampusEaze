from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ....core.dependencies import current_user
from ....database import get_db
from ....schemas.user import LoginIn, Token, UserCreate, UserOut
from ....services import auth_service
from ....utils.validators import row

router = APIRouter()


@router.post("/register", status_code=201)
def register(data: UserCreate, db: Session = Depends(get_db)):
    return row(auth_service.register(db, data), "password_hash")


@router.post("/login", response_model=Token)
def login(data: LoginIn, db: Session = Depends(get_db)):
    u, token = auth_service.login(db, data)
    return Token(access_token=token, user=UserOut.model_validate(u))


@router.get("/me", response_model=UserOut)
def me(u=Depends(current_user)):
    return u
