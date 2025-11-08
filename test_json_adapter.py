"""
Quick test to verify JSON adapter works
"""
from app.database import get_supabase, Tables
import uuid

def test_json_insert():
    """Test inserting dict into JSONB column"""
    print("Testing JSON insertion...")
    
    try:
        db = get_supabase()
        
        # Test data with dict
        test_data = {
            "id": str(uuid.uuid4()),
            "video_id": str(uuid.uuid4()),
            "status": "test",
            "full_results": {
                "test": "data",
                "nested": {
                    "value": 123
                }
            }
        }
        
        print(f"Inserting test data with dict: {test_data['full_results']}")
        
        # Try insert
        result = db.table(Tables.ANALYSIS_RESULTS).insert(test_data).execute()
        
        if result.data:
            print("✅ Insert successful!")
            print(f"   Inserted ID: {result.data[0]['id']}")
            
            # Clean up
            db.table(Tables.ANALYSIS_RESULTS).delete().eq("id", test_data["id"]).execute()
            print("   Cleaned up test data")
            return True
        else:
            print("❌ No data returned")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_json_insert()
