# Organization Management Platform — Backend

A FastAPI-based REST API powering the organization management mobile application.

The backend handles authentication, authorization, users, content, events, registrations, waitlists, notifications, and administrative operations.

---

## Responsibilities

The backend provides the core business logic and data layer for the application.

Major responsibilities include:

* User management
* Authentication and authorization
* Role-based access control
* Content management
* Lyrics management
* Character management
* Event management
* Event registration
* Waitlist management
* Notifications
* Administrative operations
* Database persistence

---

## Features

### 🔐 Authentication & Authorization

* User registration
* Login
* Firebase Authentication integration
* Email verification
* Password recovery
* Authenticated API access
* Role-based authorization
* Protected administrative endpoints

Supported roles:

```text
NORMAL_USER
PREMIUM_USER
ADMIN
SUPER_ADMIN
```

Administrative permissions are enforced at the API level.

---

## Role-Based Access Control

The backend separates permissions according to user roles.

Conceptually:

```text
NORMAL_USER
    │
    └── User-facing functionality

PREMIUM_USER
    │
    └── User functionality
        + premium functionality

ADMIN
    │
    └── Content + event administration

SUPER_ADMIN
    │
    └── Full administrative control
```

Protected routes use the existing role authorization mechanism rather than relying solely on frontend visibility.

---

## Content Management

The backend supports organization-managed content including:

* Lyrics
* Characters
* Events
* Home content
* Carousel content
* Quotes

The application is designed so that managed content can be changed without requiring a new mobile application build.

---

## Lyrics

The lyrics module supports:

* Creating lyrics
* Updating lyrics
* Deleting lyrics
* Listing lyrics
* Searching by title
* Filtering where applicable

Lyrics are exposed through REST APIs consumed by the Flutter application.

---

## Characters

The character module supports:

* Creating character entries
* Updating character information
* Deleting characters
* Listing characters
* Searching characters

---

## Events

The event system supports:

* Event creation
* Event deletion
* Event listing
* Event details
* Optional capacity limits
* User registration
* Registration management
* Waitlists

### Registration Logic

When an event has available capacity:

```text
Registration request
        ↓
Capacity available
        ↓
Registration confirmed
```

When the event is full:

```text
Registration request
        ↓
Event full
        ↓
User added to waitlist
```

When a registered slot becomes available:

```text
Cancelled registration
        ↓
Available slot
        ↓
First waitlisted user
        ↓
Automatically promoted
        ↓
Notification generated
```

The waitlist follows FIFO ordering.

---

## Notifications

The backend maintains notification records for user-facing events such as:

* Event creation
* Event updates
* Registration confirmation
* Waitlist promotion
* Other application events

The current V1 implementation provides **in-app notifications**.

Native push notification delivery is not part of the current implementation.

---

## User Management

Administrative functionality includes user management operations.

The super admin can promote users to the `ADMIN` role.

Role changes are performed through protected backend endpoints.

---

## Database

The backend uses:

**PostgreSQL**, hosted through **Neon**.

The database stores structured application data such as:

* Users
* Roles
* Events
* Registrations
* Waitlist information
* Lyrics
* Characters
* Notifications
* Application content metadata

The database does not store image binary data.

---

## Technology Stack

| Technology              | Purpose                                           |
| ----------------------- | ------------------------------------------------- |
| Python                  | Backend language                                  |
| FastAPI                 | REST API framework                                |
| SQLAlchemy              | ORM                                               |
| PostgreSQL              | Relational database                               |
| Neon                    | PostgreSQL hosting                                |
| Pydantic                | Validation and schemas                            |
| Pydantic Settings       | Configuration management                          |
| Firebase Authentication | Authentication services                           |
| JWT                     | API authentication/authorization where applicable |
| Cloudinary              | Image storage                                     |

---

## Architecture

The backend follows a modular structure separating API routes, business logic, database models, schemas, and configuration.

```text
Client
  │
  │ HTTP / REST
  ▼
FastAPI
  │
  ├── Authentication
  │
  ├── Authorization
  │
  ├── Routes
  │
  ├── Business Logic
  │
  ├── Schemas
  │
  └── Database Models
          │
          ▼
      PostgreSQL
```

---

## Project Structure

```text
app/
├── core/
│   ├── config.py
│   ├── firebase.py
│   └── security.py
│
├── api/
│   ├── routes/
│   │   ├── admin_content.py
│   │   ├── admin.py
│   │   ├── auth.py
│   │   ├── character.py
│   │   ├── content.py
│   │   ├── dashboard.py
│   │   ├── event.py
│   │   ├── lyrics.py
│   │   └── notification.py
│   └── deps.py
│
├── models/
│   ├── app_content.py
│   ├── character.py
│   ├── dashboard_image.py
│   ├── event_registration.py
│   ├── event.py
│   ├── lyrics.py
│   ├── notification.py
│   ├── roles.py
│   └── user.py
│
├── db/
│   ├── database.py
│   └── deps.py
│
├── firebase/
│   └── serviceAccountKey.json
│
├── schemas/
│   ├── character.py
│   ├── content.py
│   ├── token.py
│   ├── event.py
│   ├── lyrics.py
│   └── user.py
│
├── scripts/
│   └── create_super_admin.py
│
├── services/
│   ├── cloudinary_service.py
│   ├── notification_service.py
│   └── role_service.py
│
└── main.py
```

---

## Configuration

Application configuration is loaded using Pydantic Settings.

Sensitive configuration values are stored in environment variables rather than being hardcoded into the source code.

Example:

```env
DATABASE_URL=your_database_url
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=14
```

Never commit the actual `.env` file or production credentials.

---

## API Documentation

FastAPI automatically provides interactive API documentation.

When running locally, the documentation is available at:

```text
/docs
```

and the alternative ReDoc interface at:

```text
/redoc
```

The exact URL depends on the configured API base path.

---

## Error Handling

The API uses appropriate HTTP status codes and structured error responses for common situations such as:

* Invalid authentication
* Unauthorized access
* Forbidden role access
* Missing resources
* Invalid input
* Duplicate records
* Registration failures
* Full events
* Invalid waitlist operations
* Server/database failures

Protected operations return authorization errors rather than relying on frontend restrictions.

---

## Security Considerations

The backend follows several security principles:

* Authentication before protected operations
* Role-based authorization
* Passwords/credentials are not stored directly in source code
* Environment-based configuration
* Protected administrative endpoints
* Server-side validation
* Input validation through Pydantic
* Database-backed authorization decisions

Sensitive credentials should never be committed to the repository.

---

## Local Development

### Prerequisites

Install:

* Python 3.x
* PostgreSQL-compatible database or access to a Neon PostgreSQL database
* Git

### Create virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

On macOS/Linux:

```bash
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Setup

Create a local `.env` file containing the required configuration.

For example:

```env
DATABASE_URL=your_database_url
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=14
```

Add any Firebase configuration required by the existing authentication implementation.

**Never commit `.env` or private credentials.**

---

## Run the Server

From the backend project directory:

```bash
uvicorn app.main:app --reload
```

The API will normally be available at:

```text
http://127.0.0.1:8000
```

Interactive documentation:

```text
http://127.0.0.1:8000/docs
```

---

## API Design

The backend exposes RESTful endpoints organized by application functionality.

Conceptually:

```text
/auth
/admin-content
/lyrics
/characters
/notifications
/content
/dashboard
/admin
/events
```

The exact endpoint paths should be treated according to the current implementation.

---

## Application Flow

A simplified request flow:

```text
Flutter Client
      │
      │ HTTP Request
      ▼
FastAPI Router
      │
      ▼
Authentication
      │
      ▼
Role Authorization
      │
      ▼
Validation / Business Logic
      │
      ▼
SQLAlchemy
      │
      ▼
PostgreSQL
      │
      ▼
Response
      │
      ▼
Flutter Client
```

---

## V1 Scope

The current backend supports the core application workflows:

* Authentication
* User management
* Role-based authorization
* Lyrics
* Characters
* Home/content management
* Quotes
* Events
* Event registration
* Capacity management
* FIFO waitlists
* In-app notifications
* Administrative operations

---

## Future Scope

Potential future backend extensions include:

* Daily quiz
* Event editing workflow
* Native push notification infrastructure
* Support/query system
* Advanced analytics
* Premium-content management
* Live class/video conferencing
* Additional organization-specific workflows

These features are intentionally outside the current V1 scope.

---

## Status

**V1 — Working MVP**

The backend provides the REST API and business logic required by the Flutter application and administrative workflows.

It is structured to allow additional organization-specific functionality to be introduced without redesigning the entire application.
