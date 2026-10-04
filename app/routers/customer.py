from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import success_response
from app.dependencies import get_current_user
from app.models.customer import Customer
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.customer import (
    CustomerCreate,
    CustomerPatch,
    CustomerResponse,
    CustomerUpdate,
)

router = APIRouter(
    prefix="/api/v1/customers",
    tags=["Customers"]
)


@router.post(
    "",
    response_model=ApiResponse[CustomerResponse],
    status_code=status.HTTP_201_CREATED,
)
def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing_customer = (
        db.query(Customer)
        .filter(
            Customer.email == customer.email,
            Customer.deleted_at.is_(None),
        )
        .first()
    )

    if existing_customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer with this email already exists.",
        )

    new_customer = Customer(
        name=customer.name,
        email=customer.email,
        phone=customer.phone,
        city=customer.city,
    )

    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)

    return success_response(
        code=status.HTTP_201_CREATED,
        message="Customer created successfully.",
        data=CustomerResponse.model_validate(new_customer).model_dump(),
    )


@router.put(
    "/{customer_id}",
    response_model=ApiResponse[CustomerResponse],
)
def update_customer(
    customer_id: int,
    customer: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_customer = (
        db.query(Customer)
        .filter(
            Customer.id == customer_id,
            Customer.deleted_at.is_(None),
        )
        .first()
    )

    if not db_customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found.",
        )

    existing_email = (
        db.query(Customer)
        .filter(
            Customer.email == customer.email,
            Customer.id != customer_id,
            Customer.deleted_at.is_(None),
        )
        .first()
    )

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer with this email already exists.",
        )

    db_customer.name = customer.name
    db_customer.email = customer.email
    db_customer.phone = customer.phone
    db_customer.city = customer.city

    db.commit()
    db.refresh(db_customer)

    return success_response(
        code=status.HTTP_200_OK,
        message="Customer updated successfully.",
        data=CustomerResponse.model_validate(db_customer).model_dump(),
    )


@router.patch(
    "/{customer_id}",
    response_model=ApiResponse[CustomerResponse],
)
def patch_customer(
    customer_id: int,
    customer: CustomerPatch,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_customer = (
        db.query(Customer)
        .filter(
            Customer.id == customer_id,
            Customer.deleted_at.is_(None),
        )
        .first()
    )

    if not db_customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found.",
        )

    update_data = customer.model_dump(exclude_unset=True)

    if "email" in update_data:
        existing_customer = (
            db.query(Customer)
            .filter(
                Customer.email == update_data["email"],
                Customer.id != customer_id,
                Customer.deleted_at.is_(None),
            )
            .first()
        )

        if existing_customer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer with this email already exists.",
            )

    for key, value in update_data.items():
        setattr(db_customer, key, value)

    db.commit()
    db.refresh(db_customer)

    return success_response(
        code=status.HTTP_200_OK,
        message="Customer updated successfully.",
        data=CustomerResponse.model_validate(db_customer).model_dump(),
    )


@router.delete(
    "/{customer_id}",
    response_model=ApiResponse[None],
)
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customer = (
        db.query(Customer)
        .filter(
            Customer.id == customer_id,
            Customer.deleted_at.is_(None),
        )
        .first()
    )

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found.",
        )

    customer.deleted_at = datetime.now(UTC)

    db.commit()

    return success_response(
        code=status.HTTP_200_OK,
        message="Customer deleted successfully.",
        data=None,
    )

from math import ceil
from typing import Any


@router.get(
    "/search",
    response_model=ApiResponse[list[CustomerResponse]],
)
def search_customers(
    keyword: str = Query(..., description="Search keyword"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customers = (
        db.query(Customer)
        .filter(
            Customer.deleted_at.is_(None),
            or_(
                Customer.name.ilike(f"%{keyword}%"),
                Customer.email.ilike(f"%{keyword}%"),
                Customer.phone.ilike(f"%{keyword}%"),
                Customer.city.ilike(f"%{keyword}%"),
            ),
        )
        .order_by(Customer.id.asc())
        .all()
    )

    return success_response(
        code=status.HTTP_200_OK,
        message="Customers fetched successfully.",
        data=[
            CustomerResponse.model_validate(customer).model_dump()
            for customer in customers
        ],
    )


@router.get(
    "/{customer_id}",
    response_model=ApiResponse[CustomerResponse],
)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customer = (
        db.query(Customer)
        .filter(
            Customer.id == customer_id,
            Customer.deleted_at.is_(None),
        )
        .first()
    )

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found.",
        )

    return success_response(
        code=status.HTTP_200_OK,
        message="Customer fetched successfully.",
        data=CustomerResponse.model_validate(customer).model_dump(),
    )


@router.get(
    "",
    response_model=ApiResponse[dict[str, Any]],
)
def get_all_customers(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    city: str | None = None,
    sort_by: str = "id",
    order: str = "asc",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = (
        db.query(Customer)
        .filter(Customer.deleted_at.is_(None))
    )

    # Filtering
    if city:
        query = query.filter(Customer.city.ilike(f"%{city}%"))

    total = query.count()

    sort_columns = {
        "id": Customer.id,
        "name": Customer.name,
        "email": Customer.email,
        "city": Customer.city,
        "created_at": Customer.created_at,
    }

    sort_column = sort_columns.get(sort_by, Customer.id)

    if order.lower() == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    customers = (
        query
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    items = [
        CustomerResponse.model_validate(customer).model_dump()
        for customer in customers
    ]

    return success_response(
        code=status.HTTP_200_OK,
        message="Customers fetched successfully.",
        data={
            "items": items,
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": ceil(total / limit) if total else 0,
        },
    )