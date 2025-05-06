import os

labels = ["apple", "banana", "orange", "grape"]
out_dir = "/root/models"
name = "yolo-world_4_class_my_feature"

feature_file = os.path.join(out_dir, f"{name}.bin")
labels_file = os.path.join(out_dir, f"{name}.txt")
with open(labels_file, "w") as f:
    for label in labels:
        f.write(f"{label}\n")

cmd = f"python -u -m yolo_world_utils gen_text_feature --labels_path {labels_file} --out_feature_path {feature_file}"

print(f"Now run\n\t`{cmd}`\nto generate text feature of\n{labels}")
print("\nplease wait a moment, it may take a few seconds ...\n")
ret = os.system(cmd)
if ret != 0:
    print("[ERROR] execute have error, please see log")
else:
    print(f"saved\n\tlabels to:\n\t{labels_file}\n and text feature to:\n\t{feature_file}")
    print(f"please use yolo-world_{len(labels)}_class.mud model to run detect")

