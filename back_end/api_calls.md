# API Testing - Curl Examples

Quick reference for testing the API endpoints using curl commands.

## Test Users

| Username    | Password      | Type    | Permissions      |
| ----------- | ------------- | ------- | ---------------- |
| `acmeadmin` | `password123` | Admin   | Full access      |
| `test`      | `test123`     | Regular | List/Search only |
| `globexmgr` | `password123` | Regular | List/Search only |

## Authentication

### Login (Get JWT Token)

```bash
# Admin login
curl -X POST "http://127.0.0.1:5000/db/v1/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "acmeadmin", "password": "password123"}'

# Regular user login
curl -X POST "http://127.0.0.1:5000/db/v1/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test123"}'
```

### Validate Token

```bash
curl -X POST "http://127.0.0.1:5000/db/v1/api/auth/validate" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Logout

```bash
curl -X POST "http://127.0.0.1:5000/db/v1/api/auth/logout" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## User Operations

### List Users (Available to All)

```bash
curl -X GET "http://127.0.0.1:5000/db/v1/api/user/list" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Search Users (Available to All)

```bash
curl -X GET "http://127.0.0.1:5000/db/v1/api/user/search?q=test" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Create User (Admin Only)

```bash
curl -X POST "http://127.0.0.1:5000/db/v1/api/user/create" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ADMIN_TOKEN_HERE" \
  -d '{
    "username": "newuser",
    "password": "newpass123",
    "user_type_id": 2
  }'
```

### Update User (Admin Only)

```bash
curl -X PUT "http://127.0.0.1:5000/db/v1/api/user/update" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ADMIN_TOKEN_HERE" \
  -d '{"username": "updated_name"}'
```

### Delete User (Admin Only)

```bash
curl -X DELETE "http://127.0.0.1:5000/db/v1/api/user/delete" \
  -H "Authorization: Bearer ADMIN_TOKEN_HERE"
```

## Permission Testing

### Test Regular User Blocked from Admin Operations

```bash
# These should return "403 Forbidden" for regular users:

# Try to create user (should fail)
curl -X POST "http://127.0.0.1:5000/db/v1/api/user/create" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer REGULAR_USER_TOKEN" \
  -d '{"username": "blocked", "password": "test123"}'

# Try to update user (should fail)
curl -X PUT "http://127.0.0.1:5000/db/v1/api/user/update" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer REGULAR_USER_TOKEN" \
  -d '{"username": "blocked"}'

# Try to delete user (should fail)
curl -X DELETE "http://127.0.0.1:5000/db/v1/api/user/delete" \
  -H "Authorization: Bearer REGULAR_USER_TOKEN"
```

## Server Info

```bash
# Check server status
curl -X GET "http://127.0.0.1:5000/"

# Health check
curl -X GET "http://127.0.0.1:5000/test/hello"
```

## Expected Results

✅ **Admin users** should have access to all endpoints  
✅ **Regular users** should only access list/search endpoints  
❌ **Regular users** should get "403 Forbidden" for create/update/delete

---

## Permission Testing Examples

### Step 1: Login as Admin and Get Token

```bash
# Login as admin
curl -X POST "http://127.0.0.1:5000/db/v1/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "acmeadmin",
    "password": "password123"
  }'

# Save the token from response and use it in subsequent requests
```

### Step 2: Test Admin Privileges (Should Work)

```bash
# Create user (Admin only - should work)
curl -X POST "http://127.0.0.1:5000/db/v1/api/user/create" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ADMIN_TOKEN_HERE" \
  -d '{
    "username": "newuser",
    "password": "newpass123",
    "user_type_id": 2
  }'

# List users (Available to all - should work)
curl -X GET "http://127.0.0.1:5000/db/v1/api/user/list" \
  -H "Authorization: Bearer ADMIN_TOKEN_HERE"
```

### Step 3: Login as Regular User and Get Token

```bash
# Login as regular user
curl -X POST "http://127.0.0.1:5000/db/v1/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test",
    "password": "test123"
  }'
```

### Step 4: Test Regular User Limitations

```bash
# List users (Should work - allowed for regular users)
curl -X GET "http://127.0.0.1:5000/db/v1/api/user/list" \
  -H "Authorization: Bearer REGULAR_USER_TOKEN_HERE"

# Search users (Should work - allowed for regular users)
curl -X GET "http://127.0.0.1:5000/db/v1/api/user/search?q=test" \
  -H "Authorization: Bearer REGULAR_USER_TOKEN_HERE"

# Try to create user (Should FAIL with 403 Forbidden)
curl -X POST "http://127.0.0.1:5000/db/v1/api/user/create" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer REGULAR_USER_TOKEN_HERE" \
  -d '{
    "username": "shouldfail",
    "password": "test123",
    "user_type_id": 2
  }'

# Try to update user (Should FAIL with 403 Forbidden)
curl -X PUT "http://127.0.0.1:5000/db/v1/api/user/update" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer REGULAR_USER_TOKEN_HERE" \
  -d '{
    "username": "updated"
  }'

# Try to delete user (Should FAIL with 403 Forbidden)
curl -X DELETE "http://127.0.0.1:5000/db/v1/api/user/delete" \
  -H "Authorization: Bearer REGULAR_USER_TOKEN_HERE"
```

---

## Expected Results Summary

### ✅ Should Work for Regular Users:

- `GET /db/v1/api/user/list`
- `GET /db/v1/api/user/search`
- `POST /db/v1/api/auth/login`
- `POST /db/v1/api/auth/logout`
- `POST /db/v1/api/auth/validate`

### ❌ Should Fail (403 Forbidden) for Regular Users:

- `POST /db/v1/api/user/create`
- `PUT /db/v1/api/user/update`
- `DELETE /db/v1/api/user/delete`

### ✅ Should Work for Admin Users:

- All endpoints (full access)

---

## 1. Basic Server Health Check

### Get Server Information

```bash
curl -X GET "http://127.0.0.1:5000/" \
  -H "Content-Type: application/json"
```

### Health Check

```bash
curl -X GET "http://127.0.0.1:5000/test/hello" \
  -H "Content-Type: application/json"
```

---

## 2. Simple Authentication (Test Endpoints)

### Simple Login

```bash
curl -X POST "http://127.0.0.1:5000/test/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test",
    "password": "test123"
  }'
```

### Simple Logout

```bash
curl -X POST "http://127.0.0.1:5000/test/logout" \
  -H "Content-Type: application/json"
```

---

## 3. Database Authentication Endpoints

### Admin Login

```bash
curl -X POST "http://127.0.0.1:5000/db/v1/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "acmeadmin",
    "password": "password123"
  }'
```

### Regular User Login

```bash
curl -X POST "http://127.0.0.1:5000/db/v1/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "globexmgr",
    "password": "password123"
  }'
```

### Validate Token (Replace TOKEN with actual JWT)

```bash
curl -X POST "http://127.0.0.1:5000/db/v1/api/auth/validate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN"
```

### Logout

```bash
curl -X POST "http://127.0.0.1:5000/db/v1/api/auth/logout" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN"
```

---

## 4. User Management Endpoints

### List All Users (Available to ALL authenticated users)

#### As Admin

```bash
curl -X GET "http://127.0.0.1:5000/db/v1/api/user/list" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

#### As Regular User

```bash
curl -X GET "http://127.0.0.1:5000/db/v1/api/user/list" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer USER_TOKEN"
```

### Search Users (Available to ALL authenticated users)

#### As Admin

```bash
curl -X GET "http://127.0.0.1:5000/db/v1/api/user/search?q=acme" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

#### As Regular User

```bash
curl -X GET "http://127.0.0.1:5000/db/v1/api/user/search?q=globex" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer USER_TOKEN"
```

### Create User (ADMIN ONLY)

#### As Admin (Success)

```bash
curl -X POST "http://127.0.0.1:5000/db/v1/api/user/create" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -d '{
    "username": "newuser",
    "password": "newpassword123",
    "user_type_id": 2
  }'
```

#### As Regular User (Should Fail - 403 Forbidden)

```bash
curl -X POST "http://127.0.0.1:5000/db/v1/api/user/create" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer USER_TOKEN" \
  -d '{
    "username": "shouldfail",
    "password": "password123",
    "user_type_id": 2
  }'
```

### Update User (ADMIN ONLY)

#### As Admin

```bash
curl -X PUT "http://127.0.0.1:5000/db/v1/api/user/update" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -d '{
    "user_id": 2002,
    "username": "updateduser"
  }'
```

#### As Regular User (Should Fail - 403 Forbidden)

```bash
curl -X PUT "http://127.0.0.1:5000/db/v1/api/user/update" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer USER_TOKEN" \
  -d '{
    "user_id": 2002,
    "username": "shouldfail"
  }'
```

### Delete User (ADMIN ONLY)

#### As Admin

```bash
curl -X DELETE "http://127.0.0.1:5000/db/v1/api/user/delete" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -d '{
    "user_id": 2002
  }'
```

#### As Regular User (Should Fail - 403 Forbidden)

```bash
curl -X DELETE "http://127.0.0.1:5000/db/v1/api/user/delete" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer USER_TOKEN" \
  -d '{
    "user_id": 2002
  }'
```

---

## 5. Debug Endpoint

### Debug Login (For troubleshooting)

```bash
curl -X POST "http://127.0.0.1:5000/debug/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass"
  }'
```

---

## 6. Error Testing

### Unauthorized Access (No Token)

```bash
curl -X GET "http://127.0.0.1:5000/db/v1/api/user/list" \
  -H "Content-Type: application/json"
```

### Invalid Credentials

```bash
curl -X POST "http://127.0.0.1:5000/db/v1/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "wronguser",
    "password": "wrongpass"
  }'
```

### Invalid Token

```bash
curl -X GET "http://127.0.0.1:5000/db/v1/api/user/list" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer invalid_token_here"
```

### Missing Fields

```bash
curl -X POST "http://127.0.0.1:5000/db/v1/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "acmeadmin"
  }'
```

---

## 7. Complete Test Flow

### Step 1: Login as Admin

```bash
# Save the token from the response
ADMIN_TOKEN=$(curl -s -X POST "http://127.0.0.1:5000/db/v1/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "acmeadmin",
    "password": "password123"
  }' | jq -r '.data.token')

echo "Admin Token: $ADMIN_TOKEN"
```

### Step 2: Login as Regular User

```bash
# Save the token from the response
USER_TOKEN=$(curl -s -X POST "http://127.0.0.1:5000/db/v1/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "globexmgr",
    "password": "password123"
  }' | jq -r '.data.token')

echo "User Token: $USER_TOKEN"
```

### Step 3: Test Admin Capabilities

```bash
# List users as admin
curl -X GET "http://127.0.0.1:5000/db/v1/api/user/list" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Create user as admin
curl -X POST "http://127.0.0.1:5000/db/v1/api/user/create" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "username": "testcreated",
    "password": "password123",
    "user_type_id": 2
  }'
```

### Step 4: Test Regular User Limitations

```bash
# List users as regular user (should work)
curl -X GET "http://127.0.0.1:5000/db/v1/api/user/list" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $USER_TOKEN"

# Try to create user as regular user (should fail)
curl -X POST "http://127.0.0.1:5000/db/v1/api/user/create" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -d '{
    "username": "shouldfail",
    "password": "password123",
    "user_type_id": 2
  }'
```

---

## 8. Expected Response Formats

### Successful Login Response

```json
{
  "status": "success",
  "message": "Login successful",
  "timestamp": "2025-08-10T...",
  "data": {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
      "id": 2001,
      "username": "acmeadmin",
      "user_type_id": 1,
      "role": "Admin",
      "permissions": {
        "access_level": "admin",
        "allowed_operations": [
          "create",
          "read",
          "update",
          "delete",
          "list",
          "search",
          "manage"
        ]
      }
    },
    "expires_in": 86400
  }
}
```

### Error Response (401 Unauthorized)

```json
{
  "status": "error",
  "message": "Invalid credentials",
  "timestamp": "2025-08-10T..."
}
```

### Error Response (403 Forbidden)

```json
{
  "status": "error",
  "message": "Admin access required",
  "timestamp": "2025-08-10T..."
}
```

---

## 9. Notes

- Replace `TOKEN`, `ADMIN_TOKEN`, and `USER_TOKEN` with actual JWT tokens from login responses
- All timestamps are in UTC ISO format
- JWT tokens expire after 24 hours (86400 seconds)
- Admin users have user_type_id = 1
- Regular users have user_type_id > 1
- Use `jq` tool to parse JSON responses if available
- Server must be running on http://127.0.0.1:5000

---

## 10. Quick Test Script

Save this as `test_api.sh` for quick testing:

```bash
#!/bin/bash

BASE_URL="http://127.0.0.1:5000"

echo "=== Testing API Endpoints ==="

# Test health
echo "1. Health Check:"
curl -s "$BASE_URL/test/hello" | jq .

# Login as admin
echo -e "\n2. Admin Login:"
ADMIN_RESPONSE=$(curl -s -X POST "$BASE_URL/db/v1/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "acmeadmin", "password": "password123"}')
echo $ADMIN_RESPONSE | jq .

ADMIN_TOKEN=$(echo $ADMIN_RESPONSE | jq -r '.data.token')

# Test admin capabilities
echo -e "\n3. Admin - List Users:"
curl -s "$BASE_URL/db/v1/api/user/list" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq .

# Login as regular user
echo -e "\n4. User Login:"
USER_RESPONSE=$(curl -s -X POST "$BASE_URL/db/v1/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "globexmgr", "password": "password123"}')
echo $USER_RESPONSE | jq .

USER_TOKEN=$(echo $USER_RESPONSE | jq -r '.data.token')

# Test user limitations
echo -e "\n5. User - Try to Create (Should Fail):"
curl -s -X POST "$BASE_URL/db/v1/api/user/create" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -d '{"username": "shouldfail", "password": "test123", "user_type_id": 2}' | jq .

echo -e "\n=== Testing Complete ==="
```

Make it executable: `chmod +x test_api.sh`
Run it: `./test_api.sh`
