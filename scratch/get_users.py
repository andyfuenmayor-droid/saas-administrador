from supabase import create_client

url = "https://envojryuxdmcamlolkgp.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVudm9qcnl1eGRtY2FtbG9sa2dwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwNzY1NzMsImV4cCI6MjA4NzY1MjU3M30.0zGpypHi09GInBksu-zNAKi1k-cTHIBM39YrsEaamRc"

supabase = create_client(url, key)

candidates = [
    "datawebca@gmail.com",
    "andyfuenmayor@gmail.com",
    "admin",
    "andy",
    "Andy",
    "dataweb"
]

print("Checking 'usuarios' table for candidate users...")
for cand in candidates:
    try:
        res = supabase.table("usuarios").select("*").eq("Usuario", cand).execute()
        if res.data:
            print(f"Match found in 'usuarios' for '{cand}': {res.data}")
        else:
            print(f"No match in 'usuarios' for '{cand}'")
    except Exception as e:
        print(f"Error querying 'usuarios' for '{cand}': {e}")

print("\nChecking 'admin_users' table for candidate users...")
for cand in candidates:
    try:
        res = supabase.table("admin_users").select("*").eq("usuario", cand).execute()
        if res.data:
            print(f"Match found in 'admin_users' for '{cand}': {res.data}")
        else:
            print(f"No match in 'admin_users' for '{cand}'")
    except Exception as e:
        print(f"Error querying 'admin_users' for '{cand}': {e}")
