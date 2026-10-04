# Task 2 – Customer Management REST API

A FastAPI-based Customer Management REST API that implements user registration, JWT authentication, customer CRUD operations, search, pagination, filtering, sorting, validation, and soft deletion.

## Task Requirement

Build APIs for:

1. User Registration
2. Login (JWT)
3. Create Customer
4. Update Customer
5. Delete Customer
6. Customer Listing
7. Search Customer

### Bonus Features

- Pagination
- Filtering
- Sorting

This project implements all the required APIs and the bonus features.

---

## Features

### Authentication

- User registration
- Password hashing using bcrypt
- User login
- JWT access-token generation
- Protected customer APIs
- Token validation using OAuth2 Bearer authentication

### Customer Management

- Create customer
- Get a single customer by ID
- Update customer using PUT
- Partial update using PATCH
- Delete customer using soft delete
- List customers
- Search customers by name, email, phone, or city
- Filter customers by city
- Pagination
- Sorting by supported customer fields
- Ascending and descending sort order
- Duplicate email validation

### API Response Handling

The API uses a common response format:

```json
{
  "code": 200,
  "status": "success",
  "message": "Customers fetched successfully.",
  "data": {}
}
```

Global exception handlers are included for:

- HTTP exceptions
- Validation errors
- Unexpected server errors

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Programming language |
| FastAPI | REST API framework |
| SQLAlchemy | ORM and database interaction |
| PostgreSQL | Relational database |
| Pydantic | Request/response validation |
| python-jose | JWT creation and validation |
| Passlib + bcrypt | Password hashing |
| Uvicorn | ASGI server |
| python-dotenv | Environment variable management |
| OAuth2PasswordBearer | Bearer-token authentication |

---

## Project Structure

```text
TASK-2/
├── app/
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── response.py
│   │   ├── security.py
│   │   └── __init__.py
│   │
│   ├── models/
│   │   ├── customer.py
│   │   ├── user.py
│   │   └── __init__.py
│   │
│   ├── routers/
│   │   ├── auth.py
│   │   ├── customer.py
│   │   └── __init__.py
│   │
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── common.py
│   │   ├── customer.py
│   │   ├── user.py
│   │   └── __init__.py
│   │
│   ├── dependencies.py
│   ├── exceptions.py
│   └── main.py
│
├── .env
├── requirement.txt
└── README.md
```

> `venv/`, `__pycache__/`, and other generated files should not be committed to GitHub.

---

# Database Design

The application uses PostgreSQL with SQLAlchemy.

There are two database tables:

1. `users`
2. `customers`

## 1. Users Table

The `users` table stores registered application users.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | Primary Key | Unique user ID |
| `name` | String(100) | NOT NULL | User name |
| `email` | String(255) | UNIQUE, NOT NULL | User email |
| `password` | String(255) | NOT NULL | Bcrypt-hashed password |
| `created_at` | DateTime | Server default | Account creation time |

### Security

The plain-text password is never stored in the database. The password is hashed with bcrypt before insertion.

---

## 2. Customers Table

The `customers` table stores customer information.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | Primary Key | Unique customer ID |
| `name` | String(100) | NOT NULL | Customer name |
| `email` | String(255) | UNIQUE, NOT NULL | Customer email |
| `phone` | String(15) | NOT NULL | Customer phone number |
| `city` | String(100) | NOT NULL | Customer city |
| `created_at` | DateTime | Server default | Customer creation time |
| `updated_at` | DateTime | Server default / update | Last update time |
| `deleted_at` | DateTime | NULL | Soft-delete timestamp |

---

# ER Diagram

The project contains two database entities:

```text
┌──────────────────────────────┐
│            users             │
├──────────────────────────────┤
│ PK  id                       │
│     name                     │
│ UQ  email                    │
│     password                 │
│     created_at               │
└──────────────────────────────┘


┌──────────────────────────────┐
│          customers           │
├──────────────────────────────┤
│ PK  id                       │
│     name                     │
│ UQ  email                    │
│     phone                    │
│     city                     │
│     created_at               │
│     updated_at               │
│     deleted_at               │
└──────────────────────────────┘
```

The current implementation does **not** define a foreign-key relationship between `users` and `customers`. Users authenticate through JWT and access protected customer APIs, but customer records are not associated with a specific user in the database.

See `ER-Diagram.png` for the visual ER diagram.

---

# Authentication Flow

## User Registration

Endpoint:

```text
POST /auth/register
```

Flow:

```text
Client
   ↓
Registration Data
   ↓
Validate Input
   ↓
Check Existing Email
   ↓
Hash Password with bcrypt
   ↓
Store User in PostgreSQL
   ↓
Return User Details
```

The password is excluded from the registration response.

---

## Login

Endpoint:

```text
POST /auth/login
```

Flow:

```text
Client
   ↓
Email + Password
   ↓
Find User
   ↓
Verify Hashed Password
   ↓
Create JWT
   ↓
Return Access Token
```

The JWT contains:

- User ID (`sub`)
- User email
- Expiration time

The configured token expiration is controlled by:

```text
ACCESS_TOKEN_EXPIRE_MINUTES
```

---

# Protected APIs

Customer APIs require a valid JWT Bearer token.

In Swagger UI:

1. Open `/docs`.
2. Use the authentication/login endpoint to obtain a token.
3. Click **Authorize**.
4. Enter the Bearer token.
5. Call the protected customer endpoints.

---

# API Endpoints

## Authentication APIs

### 1. User Registration

```http
POST /auth/register
```

Example request:

```json
{
  "name": "Smit Prajapati",
  "email": "smit@example.com",
  "password": "password123"
}
```

Response:

```json
{
  "code": 201,
  "status": "success",
  "message": "User registered successfully.",
  "data": {
    "id": 1,
    "name": "Smit Prajapati",
    "email": "smit@example.com"
  }
}
```

---

### 2. Login – JWT

```http
POST /auth/login
```

Example request:

```json
{
  "email": "smit@example.com",
  "password": "password123"
}
```

Example response:

```json
{
  "code": 200,
  "status": "success",
  "message": "Login successful.",
  "data": {
    "access_token": "YOUR_JWT_TOKEN",
    "token_type": "bearer"
  }
}
```

---

# Customer APIs

All customer endpoints require:

```http
Authorization: Bearer YOUR_JWT_TOKEN
```

## 3. Create Customer

```http
POST /api/v1/customers
```

Example request:

```json
{
  "name": "Rahul Patel",
  "email": "rahul@example.com",
  "phone": "9876543210",
  "city": "Ahmedabad"
}
```

---

## 4. Update Customer

```http
PUT /api/v1/customers/{customer_id}
```

Example:

```http
PUT /api/v1/customers/1
```

Request:

```json
{
  "name": "Rahul Shah",
  "email": "rahul@example.com",
  "phone": "9876543210",
  "city": "Ahmedabad"
}
```

---

## Partial Customer Update

The project also supports:

```http
PATCH /api/v1/customers/{customer_id}
```

Only the fields that need to be changed have to be provided.

Example:

```json
{
  "city": "Surat"
}
```

---

## 5. Delete Customer

```http
DELETE /api/v1/customers/{customer_id}
```

The project uses **soft delete**.

Instead of permanently removing the database row, the API sets:

```text
deleted_at = current UTC time
```

Deleted customers are excluded from normal customer listing, search, and customer retrieval.

---

## 6. Customer Listing

```http
GET /api/v1/customers
```

Default values:

```text
page = 1
limit = 10
sort_by = id
order = asc
```

Example:

```http
GET /api/v1/customers?page=1&limit=10
```

Example response structure:

```json
{
  "code": 200,
  "status": "success",
  "message": "Customers fetched successfully.",
  "data": {
    "items": [],
    "page": 1,
    "limit": 10,
    "total": 0,
    "total_pages": 0
  }
}
```

---

# 7. Search Customer

```http
GET /api/v1/customers/search?keyword=ahmed
```

The search checks the keyword against:

- Name
- Email
- Phone
- City

The search uses case-insensitive matching.

---

# Bonus Features

## Pagination

Customer listing supports:

```text
page
limit
```

Example:

```http
GET /api/v1/customers?page=2&limit=5
```

The response contains:

- `items`
- `page`
- `limit`
- `total`
- `total_pages`

The maximum page size is limited to 100.

---

## Filtering

Customer listing supports city filtering.

Example:

```http
GET /api/v1/customers?city=Ahmedabad
```

The city filter is case-insensitive and supports partial matching.

---

## Sorting

Supported sorting fields:

```text
id
name
email
city
created_at
```

Ascending:

```http
GET /api/v1/customers?sort_by=name&order=asc
```

Descending:

```http
GET /api/v1/customers?sort_by=name&order=desc
```

If an unsupported `sort_by` value is supplied, the implementation falls back to sorting by `id`.

---

# Validation

Pydantic schemas validate incoming data.

## User

- Name: 2–100 characters
- Email: valid email format
- Password: minimum 6 characters

## Customer

- Name: 2–100 characters
- Email: valid email format
- Phone: 10–15 characters
- City: 2–100 characters

Duplicate user/customer email addresses are rejected.

---

# Security

The project implements:

- Bcrypt password hashing
- JWT access tokens
- JWT expiration
- OAuth2 Bearer authentication
- Protected customer routes
- Environment variables for database and JWT configuration
- No plain-text password storage

---

# Environment Variables

Create a `.env` file in the project root.

Example:

```env
DATABASE_URL=your_postgresql_connection_string

SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Important

Never commit the real `.env` file to GitHub.

The `.env` file contains sensitive credentials such as:

- PostgreSQL database credentials
- JWT secret key

Add `.env` to `.gitignore` before pushing the project.

---

# Installation

## 1. Open the project

```bash
cd TASK-2
```

## 2. Create a virtual environment

Windows:

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Install dependencies

The project contains the dependency file:

```text
requirement.txt
```

Install:

```bash
pip install -r requirement.txt
```

> The existing dependency file is named `requirement.txt` (singular), so use that exact filename unless you rename it.

---

# Run the Application

From the `TASK-2` project root:

```bash
uvicorn app.main:app --reload
```

The API will normally run at:

```text
http://127.0.0.1:8000
```

---

# Swagger API Documentation

FastAPI automatically provides interactive Swagger documentation at:

```text
http://127.0.0.1:8000/docs
```

Alternative ReDoc documentation:

```text
http://127.0.0.1:8000/redoc
```

Swagger can be used to test:

- Registration
- Login
- JWT authentication
- Customer creation
- Customer update
- Customer deletion
- Customer listing
- Customer search
- Pagination
- Filtering
- Sorting

---

# Database Initialization

The application creates database tables at startup using:

```python
Base.metadata.create_all(bind=engine)
```

The imported SQLAlchemy models are:

```text
User
Customer
```

No separate migration system is included in the current implementation.

---

# Main Files

### `app/main.py`

Creates the FastAPI application, registers exception handlers, includes routers, and initializes database tables.

### `app/core/config.py`

Loads environment variables.

### `app/core/database.py`

Creates:

- SQLAlchemy engine
- SessionLocal
- Declarative Base
- Database dependency

### `app/core/security.py`

Handles:

- Password hashing
- Password verification
- JWT creation

### `app/dependencies.py`

Validates the JWT Bearer token and returns the current authenticated user.

### `app/exceptions.py`

Contains global exception handlers.

### `app/models/user.py`

Defines the `users` database table.

### `app/models/customer.py`

Defines the `customers` database table.

### `app/routers/auth.py`

Contains:

- Registration API
- Login API

### `app/routers/customer.py`

Contains:

- Create customer
- Update customer
- Patch customer
- Delete customer
- Get customer
- Customer listing
- Search
- Filtering
- Pagination
- Sorting

### `app/schemas/`

Contains Pydantic request and response schemas.

---

# Testing Checklist

### Authentication

- [ ] User registration works.
- [ ] Duplicate user email is rejected.
- [ ] Password is stored as a hash.
- [ ] Login works with valid credentials.
- [ ] Invalid login credentials are rejected.
- [ ] JWT token is returned after successful login.
- [ ] Invalid/expired JWT is rejected.

### Customer APIs

- [ ] Create customer works.
- [ ] Duplicate customer email is rejected.
- [ ] Get customer by ID works.
- [ ] Update customer works.
- [ ] Partial update works.
- [ ] Delete customer works using soft delete.
- [ ] Deleted customers do not appear in normal listing.
- [ ] Customer search works.
- [ ] City filtering works.
- [ ] Pagination works.
- [ ] Sorting works.
- [ ] Ascending sorting works.
- [ ] Descending sorting works.

---

# Example API Flow

```text
1. Register User
       ↓
POST /auth/register
       ↓
2. Login
       ↓
POST /auth/login
       ↓
3. Receive JWT
       ↓
4. Authorize with Bearer Token
       ↓
5. Create Customer
       ↓
POST /api/v1/customers
       ↓
6. List / Search / Filter / Sort
       ↓
GET /api/v1/customers
GET /api/v1/customers/search
       ↓
7. Update Customer
       ↓
PUT /api/v1/customers/{id}
       ↓
8. Delete Customer
       ↓
DELETE /api/v1/customers/{id}
```

---

# Conclusion

Task 2 implements a complete **Customer Management REST API** using FastAPI, PostgreSQL, SQLAlchemy, Pydantic, bcrypt, and JWT authentication.

The project covers all required APIs:

- User Registration
- JWT Login
- Create Customer
- Update Customer
- Delete Customer
- Customer Listing
- Customer Search

It also implements all requested bonus functionality:

- Pagination
- Filtering
- Sorting

The API is protected using JWT authentication, passwords are securely hashed with bcrypt, customer deletion uses soft delete, and FastAPI Swagger documentation is available for testing the complete API.
