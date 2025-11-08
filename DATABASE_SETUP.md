# Database Setup Guide - Supabase PostgreSQL

## Step 1: Get Database Credentials from Supabase

1. Go to your Supabase Dashboard: https://supabase.com/dashboard
2. Select your project
3. Click on **Settings** (gear icon) → **Database**
4. Find the **Connection Info** section

You'll see something like:
```
Host: db.your_project_ref.supabase.co
Database name: postgres
Port: 5432
User: postgres
Password: [your-password]
```

## Step 2: Create .env File

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:
```bash
# Database Configuration (from Supabase Dashboard)
DB_USER=postgres
DB_PASSWORD=your_actual_password_here
DB_HOST=db.xxxxxxxxxxxxx.supabase.co
DB_PORT=5432
DB_NAME=postgres

# Gemini API Key (optional for AI insights)
GEMINI_API_KEY=your_gemini_key_here
```

## Step 3: Create Database Tables

### Option A: Using Supabase SQL Editor (Recommended)

1. Go to **SQL Editor** in your Supabase Dashboard
2. Click **New Query**
3. Copy the entire contents of `database_schema.sql`
4. Paste it into the SQL Editor
5. Click **Run** or press `Ctrl+Enter`
6. You should see: "Database schema created successfully!"

### Option B: Using Python Script

Create and run this script:

```python
# setup_database.py
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

# Read SQL schema
with open('database_schema.sql', 'r') as f:
    sql_schema = f.read()

# Connect and create tables
try:
    conn = psycopg2.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME")
    )
    
    cursor = conn.cursor()
    cursor.execute(sql_schema)
    conn.commit()
    
    print("✅ Database schema created successfully!")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
```

Run it:
```bash
python setup_database.py
```

## Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install `psycopg2-binary` for PostgreSQL connection.

## Step 5: Test Connection

```bash
python -c "from app.database import get_supabase; db = get_supabase(); print('✅ Database connected!')"
```

## Step 6: Verify Tables

Run this Python script to verify:

```python
from app.database import get_db_connection

with get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tables = cursor.fetchall()
    print("Tables in database:")
    for table in tables:
        print(f"  - {table[0]}")
```

Expected output:
```
Tables in database:
  - video_uploads
  - analysis_results
  - chat_history
  - analysis_complete
```

## Troubleshooting

### Connection Refused
- Check if your IP is whitelisted in Supabase Dashboard → Settings → Database → Connection Pooling
- Supabase requires connection from whitelisted IPs (use `0.0.0.0/0` for testing)

### Authentication Failed
- Double-check your password in `.env`
- Make sure you copied the **database password**, not the API keys

### Port Already in Use
- Default PostgreSQL port is 5432
- Supabase uses port 5432 by default

### SSL Certificate Error
If you get SSL errors, modify the connection:
```python
conn = psycopg2.connect(
    user=USER,
    password=PASSWORD,
    host=HOST,
    port=PORT,
    database=DBNAME,
    sslmode='require'  # Add this
)
```

## Database Tables Overview

### video_uploads
Stores uploaded video files metadata
- `id` (UUID) - Primary key
- `filename` - Original filename
- `file_path` - Server storage path
- `file_size` - File size in bytes
- `status` - Upload status
- `created_at` - Upload timestamp

### analysis_results
Stores video analysis results
- `id` (UUID) - Primary key
- `video_id` - Foreign key to video_uploads
- `results` (JSONB) - Complete analysis results
- `crowd_level` - Extracted crowd density
- `peak_count` - Maximum people count
- `ai_summary` - AI-generated insights
- `created_at` - Analysis timestamp

### chat_history
Stores chat conversations
- `id` (UUID) - Primary key
- `analysis_id` - Foreign key to analysis_results
- `role` - 'user' or 'assistant'
- `content` - Message content
- `timestamp` - Message timestamp

## Next Steps

After database setup:
1. ✅ Start the server: `uvicorn app.main:app --reload`
2. ✅ Test upload: `python test_upload_quick.py`
3. ✅ Run integration tests: `python tests/test_integration.py`

## Migration from Old Supabase Client

The new implementation is **backward compatible** with existing code:

```python
# This still works!
from app.database import get_supabase, Tables

db = get_supabase()
results = db.table(Tables.VIDEO_UPLOADS).select("*").execute()
print(results.data)
```

The difference:
- **Old**: Used `supabase-py` library (had version conflicts)
- **New**: Uses `psycopg2` directly (more stable, better performance)
- **Interface**: Same API, no code changes needed!
