# 🔧 Database Migration: Supabase SDK → PostgreSQL (psycopg2)

## ⚠️ Issue Found

**Error:** `Client.__init__() got an unexpected keyword argument 'proxy'`

**Root Cause:** Version incompatibility with `supabase-py` library. The SDK was trying to pass unsupported parameters.

## ✅ Solution Implemented

Migrated from Supabase SDK to **direct PostgreSQL connection** using `psycopg2`.

### Benefits:
- ✅ **More stable** - No SDK version conflicts
- ✅ **Better performance** - Direct database access
- ✅ **Connection pooling** - Efficient resource management
- ✅ **Backward compatible** - Same API, no code changes needed!

## 📦 What Changed

### 1. New Dependencies (`requirements.txt`)
```diff
# Database
+ psycopg2-binary==2.9.9
  supabase==2.3.0  # Now optional
```

### 2. New Configuration (`app/config.py`)
```python
# New database credentials
db_user: str
db_password: str
db_host: str
db_port: str = "5432"
db_name: str
```

### 3. New Database Module (`app/database.py`)
- **DatabasePool** - Connection pool manager
- **Database** - Supabase-compatible query builder
- **SupabaseClient** - Drop-in replacement for old client
- Same API: `get_supabase()` still works!

### 4. Environment Variables (`.env`)
```bash
# Old (not needed anymore)
# SUPABASE_URL=https://xxx.supabase.co
# SUPABASE_KEY=xxx

# New (required)
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=db.xxxxx.supabase.co
DB_PORT=5432
DB_NAME=postgres
```

### 5. Database Schema (`database_schema.sql`)
Complete SQL schema with:
- `video_uploads` table
- `analysis_results` table
- `chat_history` table
- Indexes for performance
- Auto-update triggers

## 🚀 Setup Instructions

### Quick Setup (3 steps):

1. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your Supabase database credentials
   ```

2. **Install dependencies:**
   ```bash
   pip install psycopg2-binary
   ```

3. **Setup database:**
   ```bash
   python setup_database.py
   ```

### Manual Setup:

See **DATABASE_SETUP.md** for detailed instructions.

## 🧪 Verification

Test the connection:
```bash
python -c "from app.database import get_supabase; db = get_supabase(); print('✅ Connected!')"
```

Test upload endpoint:
```bash
python test_upload_quick.py
```

Run integration tests:
```bash
python tests/test_integration.py
```

## 💡 Code Compatibility

**No changes needed in existing code!** The new implementation has the same API:

```python
# This still works exactly the same!
from app.database import get_supabase, Tables

db = get_supabase()

# Select
results = db.table(Tables.VIDEO_UPLOADS).select("*").execute()

# Insert
db.table(Tables.VIDEO_UPLOADS).insert(data).execute()

# Update
db.table(Tables.VIDEO_UPLOADS).update(data).eq("id", id).execute()

# Delete
db.table(Tables.VIDEO_UPLOADS).delete().eq("id", id).execute()
```

## 📊 Performance Improvements

| Feature | Old (Supabase SDK) | New (psycopg2) |
|---------|-------------------|----------------|
| Connection | Per-request | Pooled |
| Latency | SDK overhead | Direct SQL |
| Stability | Version conflicts | Stable |
| Type safety | SDK abstractions | Direct queries |

## 🔐 Security Notes

- ✅ Connection pooling prevents connection exhaustion
- ✅ Parameterized queries prevent SQL injection
- ✅ Credentials stored in `.env` (not in code)
- ✅ Database connections auto-closed via context managers

## 📝 Files Created/Modified

### Created:
- `database_schema.sql` - Database schema
- `setup_database.py` - Setup script
- `DATABASE_SETUP.md` - Setup guide
- `DATABASE_MIGRATION.md` - This file

### Modified:
- `app/database.py` - Complete rewrite with psycopg2
- `app/config.py` - Added DB credentials
- `requirements.txt` - Added psycopg2-binary
- `.env.example` - Updated with DB credentials

### No Changes Needed:
- All routers (`upload.py`, `analysis.py`, `chat.py`, `results.py`)
- All service files
- All test files

## ⚡ Next Steps

1. ✅ Configure `.env` with database credentials
2. ✅ Run `pip install psycopg2-binary`
3. ✅ Run `python setup_database.py`
4. ✅ Start server: `uvicorn app.main:app --reload`
5. ✅ Test: `python test_upload_quick.py`
6. ✅ Run integration tests: `python tests/test_integration.py`

## 🆘 Troubleshooting

### "ModuleNotFoundError: No module named 'psycopg2'"
```bash
pip install psycopg2-binary
```

### "connection refused"
- Check Supabase Dashboard → Settings → Database
- Whitelist your IP (or use `0.0.0.0/0` for testing)

### "authentication failed"
- Double-check password in `.env`
- Use **database password**, not API keys

### "relation does not exist"
- Run: `python setup_database.py` to create tables
- Or manually run `database_schema.sql` in Supabase SQL Editor

## ✅ Status

- [x] Database module rewritten
- [x] Configuration updated
- [x] Schema created
- [x] Setup scripts created
- [x] Documentation complete
- [ ] Test with your Supabase credentials
- [ ] Run integration tests

**Ready for testing!** 🎉
