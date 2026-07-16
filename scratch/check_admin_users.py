from supabase import create_client

url = "https://envojryuxdmcamlolkgp.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVudm9qcnl1eGRtY2FtbG9sa2dwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwNzY1NzMsImV4cCI6MjA4NzY1MjU3M30.0zGpypHi09GInBksu-zNAKi1k-cTHIBM39YrsEaamRc"

supabase = create_client(url, key)

try:
    res = supabase.table("admin_users").insert({"usuario": "test", "password_text": "test"}).execute()
    print("Insert admin_users:", res.data)
except Exception as e:
    print("Error inserting into admin_users:", e)
