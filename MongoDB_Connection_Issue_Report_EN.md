# MongoDB Connection Issue - Technical Report (English)

## Problem Summary

**Issue**: FastAPI application successfully connects to MongoDB Atlas on startup, health check endpoint shows connection is normal, but a specific API endpoint (`POST /api/v1/schedules/generate-today`) still returns "database client not initialized" error.

**Impact**: Topic generation functionality is affected, unable to generate topics via API.

**Severity**: Medium (function unavailable, but system can start)

---

## Current Status

### ✅ Working Parts

1. **Server Startup**: Server starts successfully without errors
2. **MongoDB Connection**: Successfully connects to MongoDB Atlas on startup
   - Connection string format is correct
   - Authentication successful
   - Database name correct: `ai_agent_webapp`
3. **Health Check Endpoint**: `GET /api/v1/health` returns `"database": "connected"`
4. **Configuration**: `.env` file is correctly configured with valid username and password

### ❌ Problematic Parts

1. **API Endpoint**: `POST /api/v1/schedules/generate-today` returns 400 error
   - Error message: `"資料庫客戶端未初始化"` (Database client not initialized)
   - Even though health check shows connected

---

## Root Cause Analysis

### Key Finding

**Critical Discovery**: `check_connection()` returns `(True, "connected")`, but global variables `client` and `database` remain `None` in some contexts.

### Possible Root Causes

1. **Module Reload Issue**:
   - When using `uvicorn --reload`, modules may be reloaded
   - Global variables may not be synchronized across different module instances

2. **Scope Issue**:
   - The `global` keyword may not correctly update all references
   - `client` and `database` imported by different modules may be different objects

3. **Async Execution Issue**:
   - Multiple async tasks may access global variables simultaneously
   - Race conditions may exist

4. **Connection Pool Issue**:
   - Motor client may have different instances in different processes/threads
   - Connections may be closed or reset

---

## Attempted Solutions

### 1. Configuration Fixes
- ✅ Created and configured `.env` file
- ✅ Verified MongoDB Atlas connection string format
- ✅ Confirmed username and password are correct
- ✅ Verified database name

### 2. Code Fixes

#### 2.1 Fixed `check_connection()` Function
- **Location**: `backend/app/database.py:279-320`
- **Modification**: Added automatic reconnection functionality
- **Logic**: If `client` or `database` is `None`, automatically call `connect_to_mongo()` to reconnect
- **Result**: Health check endpoint works normally, but API endpoint still has issues

#### 2.2 Fixed Health Check Endpoint
- **Location**: `backend/app/api/v1/health.py:13-28`
- **Modification**: Correctly unpack return value `(bool, str)` from `check_connection()`
- **Result**: Health check correctly displays connection status

#### 2.3 Enhanced API Endpoint
- **Location**: `backend/app/api/v1/schedules.py:256-415`
- **Modification**: Added automatic reconnection logic in `generate_today_all_topics()`
- **Result**: Problem still exists

---

## Environment Information

### System Environment
- **OS**: Windows 10 (Build 18363)
- **Python**: 3.13
- **Shell**: PowerShell

### Dependencies
- **FastAPI**: Latest
- **Motor**: 3.7.1
- **PyMongo**: Latest
- **Uvicorn**: Using `--reload` mode

### MongoDB Configuration
- **Provider**: MongoDB Atlas
- **Connection**: `mongodb+srv://`
- **Authentication**: SCRAM-SHA-1
- **Database**: `ai_agent_webapp`
- **Username**: `aadam1983119_db_user`

### Server Configuration
- **Start Command**: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
- **Environment**: `development`
- **Log Level**: `INFO`

---

## Error Messages

### API Error Response
```json
{
    "status": "failed",
    "message": "資料庫未連接，無法生成主題",
    "detail": "資料庫客戶端未初始化",
    "categories": ["fashion", "food", "trend"],
    "expected_count": 9,
    "existing_count": 0,
    "suggestion": "請配置 MONGODB_URL 並確保 MongoDB 服務正在運行"
}
```

### Health Check Response (Normal)
```json
{
    "status": "healthy",
    "environment": "development",
    "version": "1.0.0",
    "database": "connected",
    "timestamp": "2026-01-16T08:47:35.187019Z"
}
```

---

## Suggested Solutions

### 1. Use Dependency Injection
Instead of global variables, use FastAPI's dependency injection system:

```python
from fastapi import Depends
from app.database import get_database

@router.post("/generate-today")
async def generate_today_all_topics(
    db: AsyncIOMotorDatabase = Depends(get_database),
    ...
):
    # Use db instead of global database
    pass
```

### 2. Use Singleton Pattern
Create a database connection manager class:

```python
class DatabaseManager:
    _instance = None
    _client = None
    _database = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def get_database(self):
        if self._database is None:
            await self.connect()
        return self._database
```

### 3. Disable Reload Mode for Testing
Test without `--reload` to see if module reload is causing the issue:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 4. Add Detailed Logging
Add logging to track global variable state:

```python
logger.info(f"Global client id: {id(client)}, database id: {id(database)}")
logger.info(f"Client is None: {client is None}, Database is None: {database is None}")
```

---

## Files to Review

1. **Connection Management**: `backend/app/database.py`
2. **API Endpoint**: `backend/app/api/v1/schedules.py`
3. **Health Check**: `backend/app/api/v1/health.py`
4. **Configuration**: `backend/.env`
5. **Main App**: `backend/app/main.py`

---

## Next Steps

1. **Add detailed logging** to track global variable state across different module instances
2. **Test without `--reload`** to isolate module reload issues
3. **Consider refactoring** to use dependency injection instead of global variables
4. **Verify object identity** using `id()` to check if different modules reference the same objects

---

**Report Date**: 2026-01-16  
**Status**: Pending Resolution  
**Priority**: Medium

