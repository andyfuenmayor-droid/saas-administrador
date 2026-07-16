from supabase import create_client

url = "https://envojryuxdmcamlolkgp.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVudm9qcnl1eGRtY2FtbG9sa2dwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwNzY1NzMsImV4cCI6MjA4NzY1MjU3M30.0zGpypHi09GInBksu-zNAKi1k-cTHIBM39YrsEaamRc"

supabase = create_client(url, key)

try:
    print("Executing: select('*').eq('Usuario', 'admin').eq('Clave', '12345678')")
    res = supabase.table("usuarios").select("*").eq("Usuario", "admin").eq("Clave", "12345678").execute()
    print("Response Data:", res.data)
    print("Response representation:", repr(res))
except Exception as e:
    print("An exception occurred:")
    import traceback
    traceback.print_exc()
