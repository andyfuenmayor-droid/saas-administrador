import re

path = r"C:\Users\andyf\taquilla\operadora-taquilla-main\taquilla.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

styles = re.findall(r'<style>(.*?)</style>', content, re.DOTALL)
print(f"Found {len(styles)} style blocks in taquilla.py:")
for idx, style in enumerate(styles):
    print(f"\n--- STYLE BLOCK {idx+1} ---")
    print(style[:1500])
