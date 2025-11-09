"""
Database setup and verification script
Run this after configuring .env to set up your database
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os
from pathlib import Path

# Load environment variables
load_dotenv()

def test_connection():
    """Test basic database connection"""
    print("🔍 Testing database connection...")
    
    try:
        conn = psycopg2.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME")
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT NOW();")
        result = cursor.fetchone()
        
        print(f"✅ Connection successful!")
        print(f"   Server time: {result[0]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


def create_tables():
    """Create database tables from schema file"""
    print("\n📋 Creating database tables...")
    
    schema_file = Path("database_schema.sql")
    if not schema_file.exists():
        print(f"❌ Schema file not found: {schema_file}")
        return False
    
    try:
        # Read schema
        with open(schema_file, 'r') as f:
            sql_schema = f.read()
        
        # Connect and execute
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
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False


def verify_tables():
    """Verify that all required tables exist"""
    print("\n🔍 Verifying tables...")
    
    required_tables = ['video_uploads', 'analysis_results', 'chat_history']
    
    try:
        conn = psycopg2.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME")
        )
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
        """)
        
        tables = [row['table_name'] for row in cursor.fetchall()]
        
        print(f"   Found {len(tables)} tables:")
        for table in tables:
            status = "✅" if table in required_tables else "ℹ️"
            print(f"   {status} {table}")
        
        # Check if all required tables exist
        missing = [t for t in required_tables if t not in tables]
        if missing:
            print(f"\n⚠️  Missing tables: {', '.join(missing)}")
            return False
        else:
            print(f"\n✅ All required tables exist!")
            return True
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error verifying tables: {e}")
        return False


def test_operations():
    """Test basic CRUD operations"""
    print("\n🧪 Testing database operations...")
    
    try:
        from app.database import get_supabase, Tables
        
        db = get_supabase()
        print("   ✅ Database client initialized")
        
        # Test select (should work even on empty table)
        result = db.table(Tables.VIDEO_UPLOADS).select("*").limit(1).execute()
        print(f"   ✅ SELECT query works (found {len(result.data)} rows)")
        
        print("\n✅ All database operations working!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing operations: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run complete database setup and verification"""
    print("="*60)
    print(" DATABASE SETUP & VERIFICATION")
    print("="*60)
    
    # Check environment variables
    required_vars = ['DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT', 'DB_NAME']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"\n❌ Missing environment variables: {', '.join(missing_vars)}")
        print("\nPlease configure your .env file with:")
        for var in missing_vars:
            print(f"   {var}=your_value_here")
        print("\nSee DATABASE_SETUP.md for instructions.")
        return False
    
    print("✅ Environment variables configured\n")
    print(f"   Host: {os.getenv('DB_HOST')}")
    print(f"   Database: {os.getenv('DB_NAME')}")
    print(f"   User: {os.getenv('DB_USER')}")
    
    # Run tests
    if not test_connection():
        return False
    
    # Ask about creating tables
    print("\n" + "="*60)
    response = input("Create database tables? (y/N): ").strip().lower()
    if response == 'y':
        if not create_tables():
            return False
    
    if not verify_tables():
        return False
    
    if not test_operations():
        return False
    
    print("\n" + "="*60)
    print(" ✅ DATABASE SETUP COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("  1. Start server: uvicorn app.main:app --reload")
    print("  2. Test upload: python test_upload_quick.py")
    print("  3. Run integration tests: python tests/test_integration.py")
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user")
        exit(1)
