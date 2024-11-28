import os

log_path = "/maixapp/tmp/last_run.log"

if os.path.exists(log_path):
    print("LOG START:\n==============================\n\n")
    with open(log_path, "r", encoding = "utf-8") as f:
        print(f.read())
    print("\n\n==============================\nLOG END\n")
else:
    print(f"No {log_path} file found")

