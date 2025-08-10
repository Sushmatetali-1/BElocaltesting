# Authentication & Permission System Guide

## Overview

This system implements JWT-based authentication with role-based access control (RBAC) using your database schema.

## Authentication Flow

### 1. Login Process

```http
POST /db/v1/api/auth/login
Content-Type: application/json

{
    "username": "acmeadmin",
    "password": "password123"
}
```

**Response:**

```json
{
  "status": "success",
  "message": "Login successful",
  "data": {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
      "user_id": 2001,
      "username": "acmeadmin",
      "email": "admin1@acme.com",
      "name": "Alice Admin",
      "department": "IT",
      "user_type": "Admin",
      "customer_name": "Acme Corp"
    },
    "permissions": [
      {
        "app_id": 501,
        "app_title": "Acme CRM",
        "user_type": "Admin",
        "user_type_desc": "Administrator access to all modules",
        "customer_name": "Acme Corp"
      }
    ],
    "expires_in": 86400
  }
}
```

### 2. Using the Token

Include the JWT token in the Authorization header for all subsequent requests:

```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

## Permission Levels

### User Types (from user_type table)

1. **Admin** - Full access to all operations
2. **Manager** - Can manage department resources and create users
3. **Support** - Limited access, mostly read operations
4. **Developer** - Technical access
5. **Analyst** - Data analysis access
6. **Sales** - Sales-related operations
7. **Finance** - Financial operations
8. **HR** - Human resources operations
9. **Legal** - Legal and compliance
10. **Guest** - Very limited access

### Access Control Rules

#### Admin & Manager Permissions

- ✅ Create users (for their customer)
- ✅ Delete users (Admin only)
- ✅ View all users in their organization
- ✅ Access admin endpoints
- ✅ Full CRUD operations

#### Regular User Permissions

- ✅ View their own profile
- ✅ Update their own profile
- ✅ Access apps they have permission for
- ❌ Create/delete other users
- ❌ Access admin endpoints

#### Guest Permissions

- ✅ View limited data
- ❌ Modify anything
- ❌ Access sensitive endpoints

## API Endpoints & Required Permissions

### Authentication Endpoints (No auth required)

```http
POST /db/v1/api/auth/login       # Login
POST /db/v1/api/auth/validate    # Validate token
POST /db/v1/api/auth/refresh     # Refresh token
POST /db/v1/api/auth/logout      # Logout
```

### User Management Endpoints

```http
# Requires: Authentication
GET  /db/v1/api/user/profile     # Get own profile
GET  /db/v1/api/user/permissions # Get own permissions

# Requires: Authentication + Admin/Manager role
POST /db/v1/api/user/create      # Create user
GET  /db/v1/api/user/list        # List users

# Requires: Authentication + Same customer OR Admin
GET  /db/v1/api/user/{id}        # Get user by ID
PUT  /db/v1/api/user/update/{id} # Update user

# Requires: Authentication + Admin role only
DELETE /db/v1/api/user/delete/{id} # Delete user
GET  /db/v1/api/user/admin/stats   # Admin statistics

# Public (for monitoring)
GET  /db/v1/api/user/health      # Health check
```

## Testing the System

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Database

- Create your MySQL database
- Run your table creation scripts
- Run the sample data script: `sample_data.sql`

### 3. Start the Server

First, make sure your Flask server is running:

```bash
cd /Users/sohan/Downloads/BElocaltesting/back_end
./venv/bin/python app.py
```

You should see output like:

```
* Serving Flask app 'app'
* Debug mode: on
* Running on http://127.0.0.1:5000
```

### 4. Test Server is Running

```bash
curl -X GET http://127.0.0.1:5000/test/hello
```

**Expected Response:**

```json
{
  "data": {
    "server": "Flask",
    "version": "1.0"
  },
  "message": "Server is running!",
  "status": "success"
}
```

### 5. Test Simple Login (Without Database)

```bash
curl -X POST http://127.0.0.1:5000/test/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test123"}'
```

**Expected Response:**

```json
{
  "data": {
    "expires_in": 3600,
    "token": "test-token-abc123xyz",
    "user": {
      "role": "admin",
      "username": "test"
    }
  },
  "message": "Login successful",
  "status": "success"
}
```

### 6. Test Database-Based Login (Once DB is set up)

```bash
curl -X POST http://localhost:5000/db/v1/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "acmeadmin",
    "password": "password123"
  }'
```

### 7. Test Protected Endpoint

```bash
# Use the token from login response
curl -X GET http://localhost:5000/db/v1/api/user/profile \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 8. Test Admin Endpoint

```bash
# Should work with admin token
curl -X GET http://localhost:5000/db/v1/api/user/admin/stats \
  -H "Authorization: Bearer ADMIN_TOKEN_HERE"

# Should return 403 with non-admin token
curl -X GET http://localhost:5000/db/v1/api/user/admin/stats \
  -H "Authorization: Bearer REGULAR_USER_TOKEN"
```

## 🎯 Understanding Tokens & Endpoints

### What are Tokens?

- **Tokens** are like digital "keys" that prove you're authenticated
- **JWT (JSON Web Token)** is a secure way to store user information
- Think of it like a temporary ID card that expires after 24 hours
- Contains encrypted user data (user_id, permissions, expiration time)

### What are Endpoint Calls?

- **Endpoints** are specific URLs that your API responds to
- Each endpoint has a specific purpose (login, get user data, etc.)
- **HTTP methods** tell the server what action to perform:
  - `POST` = Create/Send data
  - `GET` = Retrieve data
  - `PUT/PATCH` = Update data
  - `DELETE` = Remove data

### Real-World Example:

Think of it like a hotel:

1. **Check-in (Login)**: You show ID and get a room key card
2. **Room Key (Token)**: The card has your room access encoded on it
3. **Using Facilities (API Calls)**: You swipe the card to access your room, gym, pool
4. **Expiration**: The card stops working after checkout time (token expires)

### Endpoint URL Structure:

```
http://127.0.0.1:5000/db/v1/api/user/profile
     ^              ^    ^  ^  ^   ^
     |              |    |  |  |   └─ Specific function
     |              |    |  |  └─ Module (user, auth, config)
     |              |    |  └─ API indicator
     |              |    └─ Version
     |              └─ Database/App prefix
     └─ Server address
```

### HTTP Status Codes You'll See:

- **200 OK**: Request successful
- **201 Created**: New resource created
- **400 Bad Request**: Invalid request format
- **401 Unauthorized**: Missing or invalid token
- **403 Forbidden**: Valid token but insufficient permissions
- **404 Not Found**: Endpoint or resource doesn't exist
- **500 Internal Server Error**: Server error

## Sample Test Users

| Username   | Password    | User Type | Customer   | Email                |
| ---------- | ----------- | --------- | ---------- | -------------------- |
| acmeadmin  | password123 | Admin     | Acme Corp  | admin1@acme.com      |
| globexmgr  | password123 | Manager   | Globex Inc | manager1@globex.com  |
| initechsup | password123 | Support   | Initech    | support1@initech.com |
| cyberguest | password123 | Guest     | Cyberdyne  | guest1@cyberdyne.com |

## 🛠️ Troubleshooting Common Issues

### Server Won't Start

**Problem:** `can't open file 'app.py': No such file or directory`
**Solution:** Make sure you're in the correct directory:

```bash
cd /Users/sohan/Downloads/BElocaltesting/back_end
./venv/bin/python app.py
```

### No Response from curl Commands

**Problem:** curl commands hang or return nothing
**Solution:**

1. Check if server is running: Look for "Running on http://127.0.0.1:5000"
2. Use correct URL: `http://127.0.0.1:5000` (not `localhost:5000`)
3. Test simple endpoint first: `curl -X GET http://127.0.0.1:5000/test/hello`

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'jwt'`
**Solution:** Install dependencies:

```bash
pip install PyJWT==2.8.0 bcrypt==4.0.1
```

### Database Connection Errors

**Problem:** `mysql.connector.errors.InterfaceError`
**Solution:**

1. Make sure MySQL is running
2. Create the database: `ai_chatbot`
3. Update connection string in `config.py`
4. Run sample data script: `sample_data.sql`

### Token Issues

**Problem:** `401 Unauthorized` with valid token
**Solution:**

1. Check token format: Must be `Bearer TOKEN_HERE`
2. Ensure token hasn't expired (24 hours)
3. Verify server is using same JWT secret key

### Permission Denied

**Problem:** `403 Forbidden` for admin endpoints
**Solution:**

1. Login with admin user: `acmeadmin` / `password123`
2. Use admin token for admin endpoints
3. Check user_type in database

## 🔧 Current Working Endpoints

### Test Endpoints (No Database Required)

```bash
# Check server status
GET  /test/hello

# Simple login test
POST /test/login
Body: {"username": "test", "password": "test123"}
```

### User Endpoints (Database Required)

```bash
# Health check (no auth needed)
GET  /db/v1/api/user/health

# User management (auth required)
GET  /db/v1/api/user/profile
GET  /db/v1/api/user/{id}
POST /db/v1/api/user/create
PUT  /db/v1/api/user/update/{id}
DELETE /db/v1/api/user/delete/{id}

# Admin only
GET  /db/v1/api/user/admin/stats
```

### Authentication Endpoints (When auth_routes is enabled)

```bash
POST /db/v1/api/auth/login
POST /db/v1/api/auth/validate
POST /db/v1/api/auth/refresh
POST /db/v1/api/auth/logout
```

## Security Features Implemented

### ✅ Rate Limiting

- 10 requests/minute for regular endpoints
- 5 requests/minute for auth endpoints

### ✅ JWT Token Security

- 24-hour expiration
- Includes user context
- Signature verification

### ✅ Input Validation

- JSON format validation
- Required field checking
- Email/username format validation
- Password strength checking

### ✅ Permission Checks

- User authentication verification
- Role-based access control
- Customer-level data isolation
- App-specific access control

### ✅ HTTP Status Code Enforcement

- 200: Success
- 201: Created
- 204: No Content (delete)
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 409: Conflict
- 422: Unprocessable Entity
- 429: Too Many Requests
- 500: Internal Server Error

## Production Recommendations

### 🔒 Security Enhancements

1. **Use bcrypt** instead of SHA256 for password hashing
2. **Environment variables** for JWT secret key
3. **HTTPS only** in production
4. **Token blacklisting** for logout
5. **Redis** for rate limiting and session management
6. **Input sanitization** against SQL injection
7. **CORS configuration** for frontend domains

### 📊 Monitoring & Logging

1. **Audit logs** for all authentication events
2. **Failed login attempt tracking**
3. **Permission denial logging**
4. **Performance monitoring**

### 🚀 Scalability

1. **Database connection pooling**
2. **Caching** for permission lookups
3. **Load balancing** for multiple instances
4. **Database indexes** on frequently queried fields

This system provides a solid foundation for authentication and authorization that can be extended based on your specific requirements!
