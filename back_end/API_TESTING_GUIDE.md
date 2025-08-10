# 🧪 API Testing Dashboard

## Overview

The API Testing Dashboard is a comprehensive web interface for testing the two-tier user permission system. It provides an intuitive way to authenticate users and test different API endpoints with proper permission validation.

## Features

### 1. 🔐 Authentication Component

- **User Selection**: Dropdown with pre-configured test users
- **Auto-fill Passwords**: Automatically fills password based on selected user
- **Login/Logout**: Full authentication flow with JWT token management
- **User Info Display**: Shows current user details and permissions
- **Session Persistence**: Maintains login state across page refreshes

### 2. 🚀 API Testing Component

- **Quick Endpoint Buttons**: Pre-configured buttons for common operations
- **Custom Requests**: Manual endpoint and method selection
- **Request Body Editor**: JSON editor for POST/PUT requests
- **Method Support**: GET, POST, PUT, DELETE operations
- **Auto-Authentication**: Automatically includes JWT token in requests

### 3. 📊 Response Component

- **Formatted JSON**: Pretty-printed response data
- **Response Metadata**: Status code and response time
- **Copy Function**: One-click copy to clipboard
- **Error Handling**: Clear display of errors and status codes

## Available Test Users

| Username    | Password      | User Type        | Permissions                                        |
| ----------- | ------------- | ---------------- | -------------------------------------------------- |
| `acmeadmin` | `password123` | Admin (1)        | Full access - create, update, delete, list, search |
| `test`      | `test123`     | Regular User (2) | Limited - list, search, login, logout only         |
| `globexmgr` | `password123` | Regular User (2) | Limited - list, search, login, logout only         |

## Quick Test Endpoints

### ✅ Available to All Authenticated Users

- **📋 List Users**: `GET /db/v1/api/user/list`
- **🔍 Search Users**: `GET /db/v1/api/user/search?q=test`
- **✅ Validate Token**: `POST /db/v1/api/auth/validate`

### 🔒 Admin Only (Regular users will get 403 Forbidden)

- **➕ Create User**: `POST /db/v1/api/user/create`
- **✏️ Update User**: `PUT /db/v1/api/user/update`
- **🗑️ Delete User**: `DELETE /db/v1/api/user/delete`

## How to Use

### Step 1: Access the Dashboard

Navigate to: `http://127.0.0.1:5000/api_testing`

### Step 2: Login

1. Select a user from the dropdown (acmeadmin, test, or globexmgr)
2. Password will auto-fill
3. Click "🔑 Login"
4. View user info and permissions

### Step 3: Test APIs

1. Click any of the quick endpoint buttons, or
2. Manually enter method and endpoint
3. Add request body if needed (for POST/PUT)
4. Click "🚀 Send Request"

### Step 4: View Results

- Response appears in the bottom panel
- Check status code and response time
- Copy response data if needed

## Testing Permission System

### Test Admin Privileges

1. Login as `acmeadmin`
2. Try all endpoints - all should work
3. Create a new user with the create endpoint

### Test Regular User Limitations

1. Login as `test` or `globexmgr`
2. Try list and search - should work ✅
3. Try create, update, delete - should get "Admin access required" ❌

## Technical Features

- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-time Validation**: Input validation and error handling
- **Session Management**: Maintains login state
- **Modern UI**: Clean, professional interface
- **Copy to Clipboard**: Easy sharing of API responses
- **Error Feedback**: Clear status messages and error handling

## Keyboard Shortcuts

- **Enter** in login form: Submit login
- **Ctrl+C** on response: Copy response (when focused)

## Browser Compatibility

- Chrome (recommended)
- Firefox
- Safari
- Edge

## Security Notes

- JWT tokens are stored in sessionStorage (cleared on tab close)
- All API calls include proper authentication headers
- Passwords are auto-filled for testing convenience
- CORS is enabled for development

## Troubleshooting

### Common Issues

1. **"Please login first"**: Make sure you're logged in before testing APIs
2. **"Invalid JSON"**: Check request body format for POST/PUT requests
3. **"403 Forbidden"**: Regular users trying to access admin endpoints (expected behavior)
4. **Connection errors**: Ensure Flask server is running on port 5000

### API Endpoints Summary

```
Authentication:
POST /db/v1/api/auth/login    - Login with username/password
POST /db/v1/api/auth/validate - Validate JWT token
POST /db/v1/api/auth/logout   - Logout (clear client state)

User Management:
GET  /db/v1/api/user/list     - List all users (All users)
GET  /db/v1/api/user/search   - Search users (All users)
POST /db/v1/api/user/create   - Create user (Admin only)
PUT  /db/v1/api/user/update   - Update user (Admin only)
DELETE /db/v1/api/user/delete - Delete user (Admin only)
```

---

**Happy Testing! 🚀**
