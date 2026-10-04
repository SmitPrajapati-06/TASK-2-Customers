from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import success_response
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)
from app.models.user import User
from app.schemas.auth import LoginRequest, Token
from app.schemas.common import ApiResponse
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=ApiResponse[UserResponse],
    status_code=status.HTTP_201_CREATED
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered."
        )

    db_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password)
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return success_response(
        code=status.HTTP_201_CREATED,
        message="User registered successfully.",
        data=UserResponse.model_validate(db_user).model_dump()
    )


@router.post(
    "/login",
    response_model=ApiResponse[Token]
)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.email == login_data.email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    if not verify_password(
        login_data.password,
        user.password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email
        }
    )

    token_data = Token(
        access_token=access_token,
        token_type="bearer"
    )

    return success_response(
        code=status.HTTP_200_OK,
        message="Login successful.",
        data=token_data.model_dump()
    )