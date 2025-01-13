import os

def add_file_downloads(confs : dict) -> list:
    '''
        @param confs kconfig vars, dict type
        @return list type, items is dict type
    '''
    # url = "https://phoenixnap.dl.sourceforge.net/project/asio/asio/1.28.0%20%28Stable%29/asio-1.28.0.tar.gz"
    # sha256sum = "e854a53cc6fe599bdf830e3c607f1d22fe74eee892f64c81d3ca997a80ddca97"
    # filename = "asio-1.28.0.tar.gz"

    return [
        # {
        #     'url': f'{url}',
        #     'urls': [],
        #     'sites': ['https://sourceforge.net/projects/asio/files/asio/1.28.0%20%28Stable%29/'],
        #     'sha256sum': sha256sum,
        #     'filename': filename,
        #     'path': 'asio',
        #     'check_files': [
        #         'asio-1.28.0'
        #     ]
        # }
    ]

def add_requirements(component_dirs : list):
    requires = [
        "pybind11", "python3", "basic", "nn", "peripheral", "vision", "comm", "network", "voice", "vision_extra"
    ]
    # add all components in ext_devs
    for dir in component_dirs:
        names = os.listdir(dir)
        if "ext_devs" in names:
            names = os.listdir(os.path.join(dir, "ext_devs"))
            for name in names:
                path = os.path.join(dir, "ext_devs", name)
                py_paty = os.path.join(path, "component.py")
                cmake_path = os.path.join(path, "CMakeLists.txt")
                if os.path.exists(py_paty) or os.path.exists(cmake_path):
                    requires.append(name)
            break
    return requires

