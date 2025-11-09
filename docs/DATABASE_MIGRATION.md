# 🔄 Database Migration: SQ → Supabase

## Summary

Successfully migrated the Chin  backend from SQ to Supabase (PostgreSQL) before Phase 2 implementation.

## 📋 Changes Made

### 1. Dependencies Updated

**File:** `requirements.txt`

**Removed:**
```python
aiosq==0.19.0
```

**Added:**
```python
supabase==2.3.0
postgrest==0.14.0
```

### 2. Environment Configuration Updated

**File:** `.env.example`

**Removed:**
```env
DATABASE_URL=sq:///./Chin.db
```

**Added:**
```env
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_role_key
```

### 3. Configuration Module Updated

**File:** `app/config.py`

**Changes:**
- Removed `database_url` field
- Added `supabase_url`, `supabase_key`, `supabase_service_key` fields

### 4. New Files Created

#### `app/database.py`
- Supabase client singleton pattern
- Connection management
- Table name constants
- Helper functions for database access

**Key Components:**
```python
- SupabaseClient: Singleton class for client management
- get_supabase(): Convenience function to get client
- Tables: Database table name constants
```

#### `app/schemas.py`
- Pydantic models for database tables
- Complete SQL schema for Supabase
- Table definitions and relationships

**Tables Defined:**
1. `video_uploads` - Video upload metadata
2. `analysis_results` - Analysis results storage
3. `chat_history` - Chat conversation history

**SQL Schema Includes:**
- Table creation statements
- Indexes for performance
- Row Level Security (RLS) setup
- Triggers for auto-updating timestamps
- Foreign key relationships

#### `docs/SUPABASE_SETUP.md`
Comprehensive setup guide covering:
- Account creation
- Project setup
- Schema deployment
- Connection testing
- Common operations
- Troubleshooting

### 5. Documentation Updates

**Updated Files:**
- `README.md` - Added Supabase setup instructions
- `docs/backendPRD.md` - Updated database technology
- `docs/task.md` - Updated Phase 7 tasks and completed items

## 🎯 Benefits of Supabase

### 1. **Scalability**
- Cloud-hosted PostgreSQL database
- Handles concurrent connections better than SQ
- Suitable for production deployment

### 2. **Real-time Capabilities**
- Built-in real-time subscriptions
- Useful for future features (live dashboard, notifications)

### 3. **Advanced Features**
- Full PostgreSQL feature set
- JSONB support for flexible data storage
- Full-text search capabilities
- PostGIS for geospatial data (future use)

### 4. **Built-in Security**
- Row Level Security (RLS)
- Authentication integration
- API key management

### 5. **Developer Experience**
- Web-based dashboard for data management
- SQL editor with syntax highlighting
- Automatic API generation
- Python client library

### 6. **Free Tier**
- 500MB database storage
- 1GB file storage
- 50,000 monthly active users
- Unlimited API requests

## 📊 Database Schema

### Table Relationships

```
video_uploads
    ├── id (UUID, PK)
    ├── filename
    ├── file_path
    ├── file_size
    ├── mime_type
    ├── status
    └── timestamps
    
analysis_results
    ├── id (UUID, PK)
    ├── video_id (FK → video_uploads.id)
    ├── video_name
    ├── duration_seconds
    ├── frames_processed
    ├── crowd analytics fields
    ├── bottleneck info fields
    ├── staff recommendation fields
    ├── ai_summary
    └── timestamps
    
chat_history
    ├── id (UUID, PK)
    ├── analysis_id (FK → analysis_results.id)
    ├── role (user/assistant)
    ├── content
    ├── metadata (JSONB)
    └── timestamp
```

### Cascade Deletes

- Deleting a video upload deletes its analysis results
- Deleting an analysis result deletes its chat history

## 🔧 Implementation Details

### Connection Pattern

```python
from app.database import get_supabase

# Get client
supabase = get_supabase()

# Query data
response = supabase.table('video_uploads').select('*').execute()

# Insert data
response = supabase.table('video_uploads').insert({...}).execute()

# Update data
response = supabase.table('video_uploads').update({...}).eq('id', id).execute()

# Delete data
response = supabase.table('video_uploads').delete().eq('id', id).execute()
```

### Error Handling

```python
try:
    supabase = get_supabase()
    response = supabase.table('video_uploads').select('*').execute()
    data = response.data
except ValueError as e:
    # Handle configuration errors
    print(f"Configuration error: {e}")
except Exception as e:
    # Handle database errors
    print(f"Database error: {e}")
```

## ✅ Migration Checklist

- [x] Update requirements.txt
- [x] Update .env.example
- [x] Update app/config.py
- [x] Create app/database.py
- [x] Create app/schemas.py
- [x] Create docs/SUPABASE_SETUP.md
- [x] Update README.md
- [x] Update docs/backendPRD.md
- [x] Update docs/task.md
- [x] Create migration documentation

## 🚀 Next Steps for Developers

1. **Create Supabase Account**
   - Sign up at https://supabase.com
   - Create a new project

2. **Get Credentials**
   - Copy Project URL
   - Copy anon/public key
   - Copy service_role key (optional)

3. **Configure Environment**
   - Edit `.env` file
   - Add Supabase credentials

4. **Deploy Schema**
   - Open Supabase SQL Editor
   - Run SQL from `app/schemas.py`
   - Verify tables in Table Editor

5. **Test Connection**
   - Run connection test script
   - Verify data operations work

6. **Continue with Phase 2**
   - Implement video upload API
   - Use Supabase for storing upload metadata

## 📝 Code Changes Required in Future Phases

### Phase 2: Video Upload API
```python
# Store upload metadata in Supabase
supabase = get_supabase()
video_data = {
    "id": str(uuid.uuid4()),
    "filename": file.filename,
    "file_path": upload_path,
    "file_size": file.size,
    "mime_type": file.content_type,
    "status": "pending"
}
supabase.table('video_uploads').insert(video_data).execute()
```

### Phase 7: Results Storage
```python
# Store analysis results
result_data = {
    "id": str(uuid.uuid4()),
    "video_id": video_id,
    "total_people": analytics.total_people,
    # ... other fields
}
supabase.table('analysis_results').insert(result_data).execute()
```

### Phase 6: Chat History
```python
# Store chat messages
message_data = {
    "analysis_id": analysis_id,
    "role": "user",
    "content": user_message
}
supabase.table('chat_history').insert(message_data).execute()
```

## 🆚 Comparison: SQ vs Supabase

| Feature | SQ | Supabase |
|---------|--------|----------|
| **Deployment** | Local file | Cloud-hosted |
| **Concurrent Users** | Limited | Unlimited |
| **Scaling** | Vertical only | Horizontal + Vertical |
| **Real-time** | Manual polling | Built-in subscriptions |
| **Security** | File permissions | RLS + Auth |
| **Backup** | Manual | Automatic |
| **Management UI** | None | Full dashboard |
| **Cost** | Free | Free tier + paid |
| **Best For** | Development | Production |

## 💡 Tips for Development

1. **Use Service Role Key in Backend Only**
   - Never expose in client-side code
   - Bypasses RLS policies

2. **Enable RLS for Production**
   - Protects data at database level
   - Works with Supabase Auth

3. **Use Indexes**
   - Already included in schema
   - Add more for specific queries

4. **Monitor Usage**
   - Check Supabase dashboard
   - Set up alerts for limits

5. **Test Locally First**
   - Use test project for development
   - Separate production project

## 📚 Additional Resources

- [Supabase Python Client](https://supabase.com/docs/reference/python/introduction)
- [Setup Guide](docs/SUPABASE_SETUP.md)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)

---

**Migration Status:** ✅ COMPLETE
**Ready for Phase 2:** ✅ YES
**Database:** 🟢 Supabase (PostgreSQL)
