def parse_pyi(path):
    items = {
        "class": {},
        "func": []
    }
    with open(path) as f:
        lines = f.readlines()
    class_item = None
    for i, line in enumerate(lines):
        if class_item:
            if line[0] != " ":
                items["class"][class_item["name"]] = class_item
                class_item = None
            else:
                line = line.strip()
                if line.startswith("def"):
                    class_item["func"].append(line.rsplit(":", 1)[0])
                continue

        if line.startswith("def"):
            items["func"].append(line.rsplit(":", 1)[0])
        if line.startswith("class"):
            class_item = {
                "name": line.replace("class", "").replace(":", "").strip(),
                "func": []
            }
    if class_item:
        items["class"][class_item["name"]] = class_item
    return items

if __name__ == "__main__":
    import sys
    items = parse_pyi(sys.argv[1])
    print("Class:")
    print(items["class"])
    print("Func:")
    print(items["func"])
