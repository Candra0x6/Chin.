# 🗄️ Supabase Database Setup Guide

This guide will help you set up Supabase as the database for HospiTwin Lite.

## 📋 Prerequisites

- Supabase account (free tier available)
- Project created in Supabase

## 🚀 Quick Setup Steps

### 1. Create Supabase Account

1. Go to [https://supabase.com](https://supabase.com)
2. Sign up for a free account
3. Create a new project

### 2. Get Your Credentials

After creating your project:

1. Go to **Project Settings** → **API**
2. Copy the following values:
   - **Project URL** (e.g., `https://xxxxxxxxxxxxx.supabase.co`)
   - **anon public key** (starts with `eyJ...`)
   - **service_role key** (optional, for admin operations)

### 3. Configure Environment Variables

Edit your `.env` file:

```env
# Supabase Configuration
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  # Optional
```

### 4. Create Database Schema

#### Option A: Using Supabase SQL Editor (Recommended)

1. Go to **SQL Editor** in your Supabase dashboard
2. Click **New Query**
3. Copy the SQL schema from `app/schemas.py` (the `SUPABASE_SCHEMA` constant)
4. Paste and **Run** the query

#### Option B: Using Python Script

Create and run this script:

```python
# create_tables.py
from app.schemas import SUPABASE_SCHEMA
from app.database import get_supabase

def create_tables():
    """Create database tables in Supabase."""
    supabase = get_supabase()
    
    # Note: Direct SQL execution requires service role key
    # For now, use the SQL Editor in Supabase dashboard
    print("Please run the SQL schema from app/schemas.py in Supabase SQL Editor")
    print(SUPABASE_SCHEMA)

if __name__ == "__main__":
    create_tables()
```

### 5. Verify Database Setup

Test your connection:

```python
# test_connection.py
from app.database import get_supabase

def test_connection():
    """Test Supabase connection."""
    try:
        supabase = get_supabase()
        
        # Try to query video_uploads table
        response = supabase.table('video_uploads').select('*').limit(1).execute()
        
        print("✅ Successfully connected to Supabase!")
        print(f"📊 Connection verified with table query")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()
```

## 📊 Database Schema Overview

### Tables Created

1. **video_uploads**
   - Stores uploaded video metadata
   - Fields: id, filename, file_path, file_size, mime_type, status
   - Status: pending, processing, completed, failed

2. **analysis_results**
   - Stores video analysis results
   - Fields: crowd analytics, bottleneck info, staff recommendations, AI summary
   - Linked to video_uploads via video_id

3. **chat_history**
   - Stores conversation history for AI assistant
   - Fields: analysis_id, role, content, metadata
   - Linked to analysis_results via analysis_id

### Relationships

```
video_uploads (1) ──→ (1) analysis_results
                              ↓
                              (1) ──→ (many) chat_history
```

## 🔒 Security Configuration

### Row Level Security (RLS)

The schema includes basic RLS policies. For production, customize policies:

```sql
-- Example: Restrict access to authenticated users only
CREATE POLICY "Authenticated users can read" ON video_uploads
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Authenticated users can insert" ON video_uploads
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');
```

### API Keys

- **anon key**: Safe to use in client-side code (respects RLS)
- **service_role key**: Full access, use only in backend (bypasses RLS)

## 🧪 Testing Database Operations

### Insert Test Data

```python
from app.database import get_supabase
import uuid

supabase = get_supabase()

# Insert test video upload
test_video = {
    "id": str(uuid.uuid4()),
    "filename": "test_video.mp4",
    "file_path": "uploads/test_video.mp4",
    "file_size": 1024000,
    "mime_type": "video/mp4",
    "status": "pending"
}

response = supabase.table('video_uploads').insert(test_video).execute()
print("✅ Test data inserted:", response.data)
```

### Query Data

```python
# Get all video uploads
response = supabase.table('video_uploads').select('*').execute()
print("All videos:", response.data)

# Get by status
response = supabase.table('video_uploads').select('*').eq('status', 'completed').execute()
print("Completed videos:", response.data)

# Get with join
response = (
    supabase.table('analysis_results')
    .select('*, video_uploads(*)')
    .execute()
)
print("Results with video info:", response.data)
```

## 🔧 Common Operations

### Update Record

```python
supabase.table('video_uploads').update({
    'status': 'completed'
}).eq('id', video_id).execute()
```

### Delete Record

```python
supabase.table('video_uploads').delete().eq('id', video_id).execute()
```

### Complex Query

```python
response = (
    supabase.table('analysis_results')
    .select('*')
    .gte('total_people', 20)  # Greater than or equal
    .order('created_at', desc=True)
    .limit(10)
    .execute()
)
```

## 📈 Monitoring & Maintenance

### View Data in Dashboard

1. Go to **Table Editor** in Supabase dashboard
2. Select table to view/edit data
3. Use filters and sorting

### Check Performance

1. Go to **Database** → **Query Performance**
2. Review slow queries
3. Add indexes as needed

### Backup

Supabase automatically backs up your database. To export:

1. Go to **Database** → **Backups**
2. Download backup or restore to a point in time

## 🆘 Troubleshooting

### Connection Error

```
Error: Invalid Supabase credentials
```

**Solution:** Verify `SUPABASE_URL` and `SUPABASE_KEY` in `.env`

### Table Not Found

```
Error: relation "video_uploads" does not exist
```

**Solution:** Run the SQL schema in Supabase SQL Editor

### Permission Denied

```
Error: new row violates row-level security policy
```

**Solution:** Check RLS policies or use service_role key for backend operations

### API Rate Limit

Free tier has limits. For production:
1. Upgrade to paid plan
2. Implement caching
3. Use connection pooling

## 🎯 Best Practices

1. **Use Prepared Statements**: Supabase client handles this automatically
2. **Index Frequently Queried Columns**: Already included in schema
3. **Enable RLS**: For security in production
4. **Monitor Usage**: Check dashboard regularly
5. **Handle Errors**: Always wrap database calls in try-catch
6. **Use Transactions**: For related operations that should succeed/fail together

## 📚 Additional Resources

- [Supabase Python Documentation](https://supabase.com/docs/reference/python/introduction)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Row Level Security Guide](https://supabase.com/docs/guides/auth/row-level-security)

## ✅ Checklist

- [ ] Supabase account created
- [ ] Project created in Supabase
- [ ] Credentials copied to `.env`
- [ ] SQL schema executed in SQL Editor
- [ ] Tables verified in Table Editor
- [ ] Connection tested with Python script
- [ ] Test data inserted successfully

---

**Next:** Proceed to Phase 2 - Video Upload API implementation
