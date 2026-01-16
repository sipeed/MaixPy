import os
import sys
import shutil


so_path = sys.argv[1]
project_path = sys.argv[2]

with open(os.path.join(project_path, "module_name.txt"), "r") as f:
    module_name = f.readline().strip()

dst_dir = os.path.join(project_path, module_name)
dst_path = os.path.join(dst_dir, f"_{module_name}.so")
os.makedirs(dst_dir, exist_ok=True)
shutil.copyfile(so_path, dst_path)
