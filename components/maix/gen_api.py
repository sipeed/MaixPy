'''
    @brief Generate C++ code for MaixPy API
    @license Apache 2.0
    @author Neucrack@Sipeed
    @date 2023.10.23
'''


import sys, os
import argparse
import json
import re
import yaml
import time
try:
    from .gen_api_cpp import generate_api_cpp
    from .pyi_util import parse_pyi
except Exception:
    from gen_api_cpp import generate_api_cpp
    from pyi_util import parse_pyi

def sort_headers(headers):
    # read headers_priority.txt
    headers_priority = []
    priority_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "headers_priority.txt")
    with open(priority_file, "r", encoding="utf-8") as f:
        for line in f.readlines():
            line = line.strip()
            if line.startswith("#"):
                continue
            headers_priority.append(line)
    # sort headers
    headers = sorted(headers, key = lambda x: headers_priority.index(os.path.basename(x)) if os.path.basename(x) in headers_priority else len(headers_priority))
    return headers

def find_func_def(items, name):
    for item in items:
        # def check_bool_raise(ok: bool, msg: str = '') -> None:
        funcname = item.replace("def", "").strip().split("(")[0]
        if funcname == name:
            return item
    return None

def find_class_func_def(items, mc_k, name, debug):
    item = items["class"].get(mc_k, {})
    if debug:
        print(items, items["class"], mc_k)
    if not item:
        return None
    # {"name": "", "func": {}}
    return find_func_def(item["func"], name)

def update_py_def_from_stub_files(api_tree, stub):
    '''
        parse stub files, add definition to api_tree
    '''
    maix_pyi_root = os.path.join(stub, "maix", "_maix")
    for k, v in api_tree["members"]["maix"]["members"].items():
        def parse_module(pyi_path, k, v):
            if not os.path.exists(pyi_path):
                print(f"[WARN] can not find {pyi_path}, you can build for linux platform first to generate this file")
                return
            items = parse_pyi(pyi_path)
            if v["type"] == "func":
                name = v["name"]
                func_def = find_func_def(items["func"], name)
                if func_def:
                    v["py_def"] = func_def.replace("maix._maix", "maix")
            elif v["type"] == "class":
                for mc_k, mc_v in v["members"].items():
                    if mc_v["type"] == "func":
                        func_def = find_class_func_def(items, k, mc_k, False)
                        if func_def:
                            mc_v["py_def"] = func_def.replace("maix._maix", "maix")
            for m_k, m_v in v.get("members", {}).items():
                if m_v["type"] == "func":
                    name = m_v["name"]
                    func_def = find_func_def(items["func"], name)
                    if func_def:
                        m_v["py_def"] = func_def.replace("maix._maix", "maix")
                elif m_v["type"] == "class":
                    for mc_k, mc_v in m_v["members"].items():
                        if mc_v["type"] == "func":
                            func_def = find_class_func_def(items, m_k, mc_k, False)
                            if func_def:
                                mc_v["py_def"] = func_def.replace("maix._maix", "maix")
        module_dir = os.path.join(maix_pyi_root, k)
        if os.path.isdir(module_dir):
            for m_k, m_v in v["members"].items():
                path = os.path.join(maix_pyi_root, k, f"{m_k}.pyi")
                # TODO: optimize speed
                if os.path.exists(path):
                    parse_module(path, m_k, m_v)
                else:
                    parse_module(os.path.join(maix_pyi_root, k, f"__init__.pyi"), m_k, m_v)
        else:
            parse_module(os.path.join(maix_pyi_root, f"{k}.pyi"), k, v)
    return api_tree

if __name__ == "__main__":
    print("-- Generate MaixPy C/C++ API")
    parser = argparse.ArgumentParser(description='Generate MaixPy C/C++ API')
    parser.add_argument('--vars', type=str, default="", help="CMake global variables file")
    parser.add_argument('--sdk_path', type=str, default="", help="MaixPy SDK path")
    parser.add_argument('--doc', type=str, default="", help="API documentation output file")
    parser.add_argument('--stub', type=str, default="stub", help="stub dir")
    args = parser.parse_args()

    t = time.time()

    sys.path.insert(0, os.path.join(args.sdk_path, "tools"))
    from doc_tool.gen_api import get_headers_recursive, parse_api_from_header
    from doc_tool.gen_markdown import module_to_md

    # get header files
    headers = []
    if args.vars:
        with open(args.vars, "r", encoding="utf-8") as f:
            vars = json.load(f)
        for include_dir in vars["includes"]:
            headers += get_headers_recursive(include_dir)
    else: # add sdk_path/components all .h and .hpp header files, except 3rd_party components
        except_dirs = ["3rd_party"]
        curr_dir = os.path.dirname(os.path.abspath(__file__))
        project_components_dir = os.path.abspath(os.path.join(curr_dir, ".."))
        componets_dirs = [os.path.join(args.sdk_path, "components"), project_components_dir]
        for componets_dir in componets_dirs:
            for root, dirs, files in os.walk(componets_dir):
                ignored = False
                for except_dir in except_dirs:
                    if os.path.join(componets_dir, except_dir) in root:
                        ignored = True
                        break
                if ignored:
                    continue
                for name in files:
                    path = os.path.join(root, name)
                    if path.endswith(".h") or path.endswith(".hpp"):
                        headers.append(path)
    # check each header file to find MaixPy API
    api_tree = {}
    rm = []
    all_keys = {}

    headers = sort_headers(headers)

    for header in headers:
        api_tree, updated, keys = parse_api_from_header(header, api_tree, sdks = ["maixpy"])
        if not updated:
            rm.append(header)
        for h, ks in all_keys.items():
            for k in ks:
                if k in keys:
                    raise Exception("API {} multiple defined in {} and {}".format(k, h, header))
        all_keys[header] = keys

    for r in rm:
        headers.remove(r)

    api_tree = update_py_def_from_stub_files(api_tree, args.stub)

    # generate API documentation according to api_tree
    print("-- Generating MaixPy API documentation")
    doc_out_dir = args.doc
    api_json_path = os.path.join(doc_out_dir, "api.json")
    side_bar_path = os.path.join(doc_out_dir, "sidebar.yaml")
    readme_path = os.path.join(doc_out_dir, "README.md")
    sidebar = {
        "items": [
            {
                "label": "Brief",
                "file": "README.md"
            }
        ]
    }
    with open(api_json_path, "w", encoding="utf-8") as f:
        json.dump(api_tree, f, indent=4)

    doc_maix_sidebar = {
        "label": "maix",
        "collapsed": False,
        "items": [
            # {
            #     "label": "example",
            #     "file": "maix/example.md"
            # }
        ]
    }
    sidebar["items"].append(doc_maix_sidebar)
    start_comment_template = '''
> You can use `{}` to access this module with MaixPy
> This module is generated from [MaixPy](https://github.com/sipeed/MaixPy) and [MaixCDK](https://github.com/sipeed/MaixCDK)

'''
    top_api_keys = ["maix"]
    module_members = api_tree["members"]["maix"]["members"]
    def gen_modules_doc(module_members, parents):
        sidebar_items = []
        for m, v in module_members.items():
            if v["type"] == "module":
                item = {
                        "label": m,
                        "collapsed": False,
                        "file": "{}.md".format("/".join(parents) + "/" + m)
                    }
                sidebar_items.append(item)
                api_file = os.path.join(doc_out_dir, item["file"])
                os.makedirs(os.path.dirname(api_file), exist_ok = True)
                module_full_name = ".".join(parents + [m])
                start_comment = start_comment_template.format(module_full_name, module_full_name)
                content = module_to_md(parents, m, v, start_comment, module_join_char = ".")
                with open(api_file, "w", encoding="utf-8") as f:
                    f.write(content)
                # find submodule
                for _k, _v in v["members"].items():
                    if _v["type"] == "module":
                        item["items"] = gen_modules_doc(v["members"], parents + [m])
        return sidebar_items
    sidebar_items = gen_modules_doc(module_members, top_api_keys)
    doc_maix_sidebar["items"] += sidebar_items
    with open(side_bar_path, "w", encoding="utf-8") as f:
        yaml.dump(sidebar, f, indent=4)

    readme = '''
---
title: MaixPy API -- Maix AI machine vision platform Python API
---

**You can read API doc at [MaixPy API on Sipeed Wiki](https://wiki.sipeed.com/maixpy/api/index.html)**

If you want to **preview API doc offline**, two ways:
1. Download offline doc files from [Releases page](https://github.com/sipeed/MaixPy/releases), file name is `maixpy_vx.x.x_doc.zip`.
2. Build MaixPy, and API doc will be generated in `MaixPy/docs/api/` directory.

> For MaixPy developer: This API documentation is generated from the source code, DO NOT edit this file manually!

MaixPy API documentation, modules:

'''
    readme += "| module | brief |\n"
    readme += "| --- | --- |\n"
    for m, v in module_members.items():
        # add link to module api doc
        readme += "|[maix.{}](./maix/{}.md) | {} |\n".format(m, m,
                        v["doc"].replace("\n", "<br>") if type(v["doc"]) == str else v["doc"]["brief"].replace("\n", "<br>")
                    )
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme)

    print("-- Generate MaixPy API doc complete ({:.2f}s)".format(time.time() - t))