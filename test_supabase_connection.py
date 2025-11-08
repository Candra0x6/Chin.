"""
Test script to verify Supabase connection and setup.
Run this after setting up Supabase to ensure everything works.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from app.database import get_supabase, Tables
from app.config import settings


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def test_configuration():
    """Test if Supabase configuration is present."""
    print_section("1. Testing Configuration")
    
    try:
        print(f"✓ Supabase URL: {settings.supabase_url[:30]}..." if settings.supabase_url else "✗ Missing SUPABASE_URL")
        print(f"✓ Supabase Key: {'*' * 20}...{settings.supabase_key[-10:]}" if settings.supabase_key else "✗ Missing SUPABASE_KEY")
        
        if not settings.supabase_url or not settings.supabase_key:
            print("\n❌ Configuration Error: Missing Supabase credentials")
            print("Please add SUPABASE_URL and SUPABASE_KEY to your .env file")
            return False
        
        print("\n✅ Configuration OK")
        return True
    except Exception as e:
        print(f"\n❌ Configuration Error: {e}")
        return False


def test_connection():
    """Test connection to Supabase."""
    print_section("2. Testing Connection")
    
    try:
        supabase = get_supabase()
        print("✓ Supabase client created successfully")
        print(f"✓ Connected to: {settings.supabase_url}")
        print("\n✅ Connection OK")
        return True
    except ValueError as e:
        print(f"\n❌ Connection Error: {e}")
        print("Please check your Supabase credentials in .env file")
        return False
    except Exception as e:
        print(f"\n❌ Connection Error: {e}")
        return False


def test_tables():
    """Test if database tables exist."""
    print_section("3. Testing Database Tables")
    
    try:
        supabase = get_supabase()
        
        # Test each table
        tables_to_test = [
            Tables.VIDEO_UPLOADS,
            Tables.ANALYSIS_RESULTS,
            Tables.CHAT_HISTORY
        ]
        
        all_tables_exist = True
        
        for table_name in tables_to_test:
            try:
                # Try to query the table (with limit 0 to avoid fetching data)
                response = supabase.table(table_name).select('*').limit(0).execute()
                print(f"✓ Table '{table_name}' exists")
            except Exception as e:
                print(f"✗ Table '{table_name}' not found: {str(e)[:50]}...")
                all_tables_exist = False
        
        if all_tables_exist:
            print("\n✅ All tables exist")
            return True
        else:
            print("\n❌ Some tables are missing")
            print("Please run the SQL schema from app/schemas.py in Supabase SQL Editor")
            print("See docs/SUPABASE_SETUP.md for instructions")
            return False
            
    except Exception as e:
        print(f"\n❌ Table Check Error: {e}")
        return False


def test_insert_read_delete():
    """Test basic database operations."""
    print_section("4. Testing Database Operations")
    
    try:
        supabase = get_supabase()
        
        # Test data
        test_video = {
            "filename": "test_connection.mp4",
            "file_path": "uploads/test_connection.mp4",
            "file_size": 1024,
            "mime_type": "video/mp4",
            "status": "test"
        }
        
        # INSERT test
        print("Testing INSERT...")
        insert_response = supabase.table(Tables.VIDEO_UPLOADS).insert(test_video).execute()
        
        if not insert_response.data:
            print("✗ INSERT failed: No data returned")
            return False
        
        test_id = insert_response.data[0]['id']
        print(f"✓ INSERT successful (ID: {test_id})")
        
        # READ test
        print("Testing SELECT...")
        read_response = supabase.table(Tables.VIDEO_UPLOADS).select('*').eq('id', test_id).execute()
        
        if not read_response.data:
            print("✗ SELECT failed: No data returned")
            return False
        
        print(f"✓ SELECT successful (Found record with ID: {test_id})")
        
        # DELETE test (cleanup)
        print("Testing DELETE...")
        delete_response = supabase.table(Tables.VIDEO_UPLOADS).delete().eq('id', test_id).execute()
        print(f"✓ DELETE successful (Cleaned up test record)")
        
        print("\n✅ All database operations working")
        return True
        
    except Exception as e:
        print(f"\n❌ Database Operation Error: {e}")
        print("\nThis could be due to:")
        print("- RLS (Row Level Security) policies blocking operations")
        print("- Missing table columns")
        print("- Network connectivity issues")
        return False


def run_all_tests():
    """Run all tests in sequence."""
    print("\n" + "="*60)
    print("  🏥 HospiTwin Lite - Supabase Connection Test")
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(("Configuration", test_configuration()))
    
    if results[-1][1]:  # Only continue if configuration is OK
        results.append(("Connection", test_connection()))
    
    if results[-1][1]:  # Only continue if connection is OK
        results.append(("Tables", test_tables()))
    
    if results[-1][1]:  # Only continue if tables exist
        results.append(("Operations", test_insert_read_delete()))
    
    # Print summary
    print_section("Test Summary")
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:20s} {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*60)
    
    if all_passed:
        print("🎉 All tests passed! Supabase is ready to use.")
        print("\nNext steps:")
        print("1. Continue with Phase 2: Video Upload API")
        print("2. Run: python -m app.main")
        print("3. Access API docs: http://localhost:8000/docs")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        print("\nRefer to docs/SUPABASE_SETUP.md for help.")
    
    print("="*60 + "\n")
    
    return all_passed


if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)
