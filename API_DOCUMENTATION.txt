# A.I.ncident API Documentation

## this is a high-level reference, refer to built-in Swagger at /docs



The A.I.ncident API is a RESTful service built with FastAPI that provides comprehensive incident management capabilities for retail stores. The API supports user authentication, role-based access control, incident reporting, AI-powered analysis, CSV export functionality, and Stripe billing integration.

**Base URL**: `http://localhost:8000` (development)  
**API Version**: 1.0.0  
**Authentication**: JWT Bearer Token

## Table of Contents

1. [Authentication](#authentication)
2. [User Management](#user-management)
3. [Incident Management](#incident-management)
4. [Data Export](#data-export)
5. [Billing & Subscriptions](#billing--subscriptions)
6. [Error Handling](#error-handling)
7. [Rate Limiting](#rate-limiting)

## Authentication

### Login
**POST** `/api/login`

Authenticate a user and receive a JWT access token.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Status Codes:**
- `200 OK`: Successful authentication
- `401 Unauthorized`: Invalid credentials

### Get Current User
**GET** `/api/me`

Retrieve information about the currently authenticated user.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "role": "admin",
  "subscription_status": "active",
  "plan_id": "enterprise",
  "store": {
    "id": 1,
    "store_number": "Store #001",
    "name": "Downtown Store",
    "location": "123 Main St"
  }
}
```

## User Management

### Register User
**POST** `/api/register`

Create a new user account.

**Request Body:**
```json
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "SecurePass123!",
  "role": "employee",
  "store_id": 1
}
```

**Validation Rules:**
- Username: 3-20 characters, alphanumeric + underscore
- Password: Minimum 8 characters, requires uppercase, lowercase, digits, and special characters
- Email: Valid email format (optional)

### Create User (Admin Only)
**POST** `/api/users/create`

Create a new user with role-based permissions.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "SecurePass123!",
  "role": "staff",
  "store_id": 1
}
```

**Role Permissions:**
- **Admin**: Can create all roles (admin, staff, employee)
- **Pro Users**: Can create staff and employee roles (max 5 users per plan)
- **Employees**: Cannot create users

### List Users
**GET** `/api/users?skip=0&limit=50`

Retrieve a list of users (admin only).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `skip` (int): Number of records to skip (default: 0)
- `limit` (int): Maximum number of records to return (default: 50, max: 100)

### Update User
**PUT** `/api/users/{user_id}`

Update user information (admin only).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "username": "updateduser",
  "email": "updated@example.com",
  "role": "staff",
  "store_id": 2
}
```

### Delete User
**DELETE** `/api/users/{user_id}`

Delete a user account (admin only).

**Headers:**
```
Authorization: Bearer <access_token>
```

### Change Password
**POST** `/api/users/change-password`

Change the current user's password.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "current_password": "OldPass123!",
  "new_password": "NewSecurePass456!"
}
```

## Incident Management

### Create Incident
**POST** `/api/incidents/`

Create a new incident report.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Form Data:**
- `description` (string, required): Detailed incident description (10-2000 chars)
- `store` (string, required): Store name in format "Store #XXX"
- `location` (string, required): Specific location within store (2-100 chars)
- `offender` (string, required): Offender description (2-100 chars)
- `file` (file, optional): Incident image (PNG, JPG, JPEG, max 5MB)

**Response:**
```json
{
  "id": 1,
  "timestamp": "2025-07-15T10:30:00",
  "description": "Customer attempted to steal merchandise",
  "summary": "AI-generated summary of the incident",
  "tags": "theft,security,customer",
  "severity": "medium",
  "store_name": "Store #001",
  "location": "Electronics section",
  "offender": "Male, 25-30, blue jacket",
  "pdf_path": "/static/reports/incident_1_20250715103000.pdf",
  "image_url": "/static/images/abc123.png",
  "user_id": 1,
  "reported_by": "john_doe"
}
```

### Get All Incidents
**GET** `/api/incidents/?skip=0&limit=50&store_id=1&tag=theft`

Retrieve incidents with filtering and pagination.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `skip` (int): Number of records to skip (default: 0)
- `limit` (int): Maximum number of records (default: 50, max: 100)
- `store_id` (int, optional): Filter by store ID
- `tag` (string, optional): Filter by incident tag
- `offender_id` (int, optional): Filter by offender ID

**Role-Based Access:**
- **Admin**: Can view all incidents
- **Staff/Employee**: Can only view incidents from their assigned store

### Get Incident by ID
**GET** `/api/incidents/{incident_id}`

Retrieve a specific incident by ID.

**Headers:**
```
Authorization: Bearer <access_token>
```

### Delete Incident
**DELETE** `/api/incidents/{incident_id}`

Delete an incident (admin/staff only).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Role-Based Access:**
- **Admin**: Can delete any incident
- **Staff**: Can only delete incidents from their assigned store
- **Employee**: Cannot delete incidents

### Get Accessible Stores
**GET** `/api/incidents/stores/accessible`

Get list of stores the current user can access.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
[
  {
    "id": 1,
    "store_number": "Store #001",
    "name": "Downtown Store",
    "location": "123 Main St"
  }
]
```

### Get Pagination Info
**GET** `/api/incidents/pagination-info`

Get pagination metadata for incidents.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `store_id` (int, optional): Filter by store ID
- `tag` (string, optional): Filter by incident tag
- `offender_id` (int, optional): Filter by offender ID

### Download Incident PDF
**GET** `/api/incident/{incident_id}/pdf`

Download the PDF report for a specific incident.

**Headers:**
```
Authorization: Bearer <access_token>
```

## Data Export

### Export Incidents CSV
**GET** `/api/incidents/export-csv`

Export filtered incidents and graph data as CSV file.

**Headers:**
```
Authorization: Bearer <access_token>
Accept: text/csv
```

**Query Parameters:**
- `skip` (int): Number of records to skip (default: 0)
- `limit` (int): Maximum number of records (default: 1000, max: 5000)
- `store_id` (int, optional): Filter by store ID
- `tag` (string, optional): Filter by incident tag
- `offender_id` (int, optional): Filter by offender ID
- `start_date` (string, optional): Start date filter (ISO format: YYYY-MM-DD)
- `end_date` (string, optional): End date filter (ISO format: YYYY-MM-DD)

**Role-Based Access:**
- **Admin**: Can export all incidents
- **Staff**: Can only export incidents from their assigned store
- **Employee**: Cannot export incidents

**Response:**
- **Content-Type**: `text/csv`
- **Content-Disposition**: `attachment; filename=incidents_export_YYYYMMDD_HHMMSS.csv`

**CSV Format:**
```csv
ID,Timestamp,Description,Summary,Tags,Severity,Store Name,Location,Offender,PDF Path,Image URL,User ID,Reported By
1,2025-07-15 10:30:00,Customer attempted to steal merchandise,AI-generated summary,theft,3,Store #001,Electronics,Male 25-30 blue jacket,/static/reports/incident_1.pdf,/static/images/abc123.png,1,john_doe

--- Incident Counts by Date ---
Date,Count
2025-07-15,5
2025-07-14,3

--- Incident Counts by Severity ---
Severity,Count
3,4
4,2
5,2
```

**Features:**
- Includes all incident data with applied filters
- Adds summary statistics (counts by date and severity)
- Respects RBAC permissions
- Supports date range filtering
- Large export capacity (up to 5000 records)

## Billing & Subscriptions

### Get Available Plans
**GET** `/api/billing/plans`

Retrieve all available subscription plans.

**Response:**
```json
{
  "plans": {
    "basic": {
      "name": "Basic Plan",
      "price": 29.99,
      "features": ["Up to 100 incidents/month", "Basic reporting"],
      "limits": {"incidents_per_month": 100, "users": 1}
    },
    "pro": {
      "name": "Pro Plan", 
      "price": 99.99,
      "features": ["Up to 1000 incidents/month", "Advanced analytics", "Up to 5 users"],
      "limits": {"incidents_per_month": 1000, "users": 5}
    },
    "enterprise": {
      "name": "Enterprise Plan",
      "price": 299.99,
      "features": ["Unlimited incidents", "All features", "Unlimited users"],
      "limits": {"incidents_per_month": -1, "users": -1}
    }
  }
}
```

### Get My Subscription
**GET** `/api/billing/my-subscription`

Get current user's subscription details.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "subscription": {
    "status": "active",
    "plan_id": "pro"
  },
  "plan": {
    "name": "Pro Plan",
    "price": 99.99,
    "features": ["Up to 1000 incidents/month", "Advanced analytics"]
  },
  "features": ["incident_analytics", "pdf_reports", "image_uploads"],
  "limits": {"incidents_per_month": 1000, "users": 5}
}
```

### Create Checkout Session
**POST** `/api/billing/create-checkout-session`

Create a Stripe checkout session for subscription.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "plan_id": "pro"
}
```

**Response:**
```json
{
  "checkout_url": "https://checkout.stripe.com/pay/cs_test_...",
  "message": "Checkout session created successfully"
}
```

### Create Billing Portal Session
**POST** `/api/billing/billing-portal`

Create a billing portal session for customer management.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "portal_url": "https://billing.stripe.com/session/...",
  "message": "Billing portal session created"
}
```

### Cancel Subscription
**POST** `/api/billing/cancel-subscription`

Cancel the current subscription.

**Headers:**
```
Authorization: Bearer <access_token>
```

### Get Usage Statistics
**GET** `/api/billing/usage`

Get current usage statistics.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "incidents_this_month": 45,
  "incidents_limit": 1000,
  "users_count": 3,
  "users_limit": 5,
  "usage_percentage": 4.5
}
```

### Stripe Webhook
**POST** `/api/billing/webhook`

Handle Stripe webhook events (subscription updates, payment failures, etc.).

**Headers:**
```
Stripe-Signature: t=1234567890,v1=abc123...
```

## Error Handling

The API uses standard HTTP status codes and returns detailed error messages.

### Error Response Format
```json
{
  "detail": "Error message description",
  "type": "validation_error",
  "errors": [
    {
      "field": "username",
      "message": "Username must be between 3 and 20 characters"
    }
  ]
}
```

### Common Status Codes
- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Default**: 100 requests per minute per IP address
- **Configurable**: Via `RATE_LIMIT_REQUESTS` environment variable
- **Headers**: Rate limit information included in response headers

### Rate Limit Headers
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642234567
```

## Security Features

### Authentication
- JWT tokens with configurable expiration
- Secure password hashing using bcrypt
- Role-based access control (RBAC)

### Input Validation
- Comprehensive input sanitization
- File upload validation (type, size limits)
- SQL injection prevention via SQLAlchemy ORM

### CORS Configuration
- Configurable allowed origins
- Secure cookie handling
- Preflight request support

### Environment Variables
Required environment variables for production:

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/dbname

# Security
SECRET_KEY=your-secure-jwt-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# External Services
OPENAI_API_KEY=your-openai-api-key
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_WEBHOOK_SECRET=your-stripe-webhook-secret

# Environment
ENVIRONMENT=production
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

## Testing

The API includes comprehensive test coverage:

```bash
# Run tests
cd backend
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html
```

## Support

For API support and questions:
- **Documentation**: This document
- **Health Check**: `GET /` - Returns API status
- **OpenAPI Docs**: `GET /docs` - Interactive API documentation
- **ReDoc**: `GET /redoc` - Alternative API documentation

---

*Last updated: July 2025*  
*API Version: 1.0.0*

## 🚀 Optimized Dashboard Data Endpoint

### `GET /api/incidents/dashboard-data`

**Description:**
Fetch all dashboard data (incidents, pagination info, and accessible stores) in a single optimized API call. This endpoint is designed to speed up dashboard loading by reducing the number of separate API requests.

**Authentication:**
- Requires Bearer JWT token (same as other endpoints)

**Query Parameters:**
- `skip` (int, optional): Number of records to skip (for pagination)
- `limit` (int, optional): Number of records to return (default: 50)
- `store_id` (int, optional): Filter by store ID
- `tag` (str, optional): Filter by tag
- `offender_id` (int, optional): Filter by offender ID

**Response:**
```json
{
  "incidents": [ ... ],           // List of incident objects (same as /incidents/)
  "pagination": {
    "total": 123,                 // Total number of incidents
    "pages": 3                    // Number of pages (50 per page)
  },
  "accessible_stores": [ ... ]    // List of stores user can access
}
```

**Notes:**
- RBAC and subscription checks are enforced as with other endpoints.
- This endpoint replaces the need to call `/incidents/`, `/incidents/pagination-info`, and `/incidents/stores/accessible` separately for the dashboard.

## 🧩 Frontend Utility: `get_dashboard_data`

A new utility function is available in `frontend/utils/api.py`:

```python
def get_dashboard_data(token: str, skip: int = 0, limit: int = 50) -> dict:
    """Get all dashboard data in a single optimized call."""
```
- This function calls the new endpoint and returns all dashboard data for use in the frontend.

---

*Last updated: July 2025*  
*API Version: 1.0.0* 