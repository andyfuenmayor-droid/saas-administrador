from supabase import create_client

url = "https://envojryuxdmcamlolkgp.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVudm9qcnl1eGRtY2FtbG9sa2dwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwNzY1NzMsImV4cCI6MjA4NzY1MjU3M30.0zGpypHi09GInBksu-zNAKi1k-cTHIBM39YrsEaamRc"
supabase = create_client(url, key)

try:
    res = supabase.auth.sign_up({"email": "test_nonexistent_email_12345@example.com", "password": "password123"})
    print("Success:", res)
except Exception as e:
    print("Error:", e)
