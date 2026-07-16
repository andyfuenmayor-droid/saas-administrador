from supabase import create_client

url = "https://envojryuxdmcamlolkgp.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVudm9qcnl1eGRtY2FtbG9sa2dwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjA3NjU3MywiZXhwIjoyMDg3NjUyNTczfQ.RgfpYk7MSpfuOMy0mPtQiK838Ao1z38c1r7-bxcU-7E"
supabase = create_client(url, key)

try:
    res = supabase.auth.admin.delete_user('5bcb1436-3303-451e-92e6-5ae9460b1095')
    print("Deleted user successfully:", res)
except Exception as e:
    print("Error deleting user:", e)
