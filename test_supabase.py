# Updated test_supabase.py
from supabase_client import supabase

def test_supabase_connection():
    try:
        # Query the "patients" table
        response = supabase.table("patients").select("*").execute()
        
        # Check if data exists
        if response.data:
            print("✅ Data retrieved successfully:")
            print(response.data)
        else:
            print("⚠️ No data found in 'patients' table")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_supabase_connection()