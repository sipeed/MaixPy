#!/usr/bin/env python
#-*- coding = utf-8 -*-

#
# @file from https://github.com/Neutree/c_cpp_project_framework
# @author neucrack
# @license Apache 2.0
#

import sys, os

def is_project_valid():
    return os.path.exists("main")

def get_sdk_path():
    sdk_path = None
    sdk_env_name = "MAIXCDK_PATH"

    # 1. get SDK absolute path from MAIXCDK_PATH env
    try:
        if os.environ[sdk_env_name] and os.path.exists(os.environ[sdk_env_name]):
            sdk_path = os.environ[sdk_env_name]
    except Exception:
        pass

    # 2. check if in MaixCDK repo, higher priority
    path = os.path.abspath("../../")
    if os.path.exists(path+"/tools/cmake/project.py"):
        sdk_path = path

    # 3. check if MaixCDK path valid
    if not sdk_path or not os.path.exists(sdk_path):
        print("")
        print("Error: can not find MaixCDK, please set MAIXCDK_PATH env to MaixCDK directory")
        print("")
        sys.exit(1)
    return os.path.abspath(sdk_path)

def exec_project_py():
    # 1. check main component
    if not is_project_valid():
        print("")
        print("Error: can not find main component, please execute this command in your project root directory")
        print("")
        sys.exit(1)

    # 2. get MaixCDK path
    sdk_path = get_sdk_path()
    print("-- SDK_PATH:{}".format(sdk_path))
    project_path = os.path.abspath(".")

    # 3. execute project script from SDK
    project_file_path = sdk_path+"/tools/cmake/project.py"
    sys.path.insert(0, os.path.dirname(project_file_path))
    from project import main
    main(sdk_path, project_path)

def main():
    exec_project_py()

if __name__ == "__main__":
    main()
