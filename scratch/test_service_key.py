from supabase import create_client

url = "https://envojryuxdmcamlolkgp.supabase.co"
# Using the service key now!
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVudm9qcnl1eGRtY2FtbG9sa2dwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjA3NjU3MywiZXhwIjoyMDg3NjUyNTczfQ.RgfpYk7MSpfuOMy0mPtQiK838Ao1z38c1r7-bxcU-7E"

try:
    supabase = create_client(url, key)
    res = supabase.table("usuarios").select("*").execute()
    print("Usuarios data using service key:")
    print(res.data)
except Exception as e:
    print(f"Error querying table with service key: {e}")
