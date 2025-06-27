import os

print("[DEBUG] Checking PATH:")
for p in os.environ["PATH"].split(";"):
    print(p)

print("[DEBUG] Checking cudnn_ops64_9.dll location...")

dll_found = False
for path in os.environ["PATH"].split(";"):
    dll_path = os.path.join(path, "cudnn64_8.dll")
    if os.path.exists(dll_path):
        print(f"[DEBUG] Found cudnn_ops64_8.dll in: {path}")
        dll_found = True
        break

if not dll_found:
    print("[ERROR] cudnn64_8.dll NOT found in any PATH location!")
