import os
import sys

print("=== DEBUG INFO ===")
print("Current directory:", os.getcwd())
print("Directory contents:", os.listdir('.'))
print("Python path:", sys.path)

try:
    from tplab2.wsgi import application
    print("✅ SUCCESS: tplab2.wsgi imported successfully!")
except ImportError as e:
    print("❌ ERROR importing tplab2.wsgi:", e)
    print("Available modules:")
    for item in os.listdir('.'):
        if os.path.isdir(item):
            print(f" - {item}/")
            try:
                print(f"   Contents: {os.listdir(item)}")
            except:
                print(f"   Cannot list contents")