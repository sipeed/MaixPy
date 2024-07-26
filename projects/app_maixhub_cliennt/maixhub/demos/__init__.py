import os
from . import yolov5, classifier
import configparser

codes = {
    "classifier": classifier,
    "yolov5": yolov5,
}

def read_model_type_from_mud(mud):
    config = configparser.ConfigParser()
    config.read(mud)
    model_type = config.get("extra", "model_type", fallback=None)
    return model_type

def load_mud_model(model_path, init_model = True):
    print(model_path)
    model_type = read_model_type_from_mud(model_path)
    if (not model_type) or model_type not in codes.keys():
        return None, "mode not support", None
    try:
        obj = codes[model_type].Demo(model_path)
        if init_model:
            obj.init()
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None, "Load error", None
    return model_path, model_type, obj

def load_model_info(model_dir_path, init_model = True):
    '''
        @model_dir model files dir, should include report.json
        @return model_dir, report_info:dict, code_object
    '''
    print("load_model_info", model_dir_path)
    if os.path.isfile(model_dir_path):
        return load_mud_model(model_dir_path, init_model)
    files = os.listdir(model_dir_path)
    model_path = None
    for name in files:
        if name.endswith(".mud"):
            model_path = os.path.join(model_dir_path, name)
            break
    if not model_path:
        return None, "No mud file found", None
    return load_mud_model(model_path, init_model)


def load_saved_models(models_dir):
    '''
        @return models list: [
            {
                "name": "xxxx",
                "path": "xxxx.mud",
                "model_type": "yolov5",
                "is_dir": False
            }
        ]
    '''
    models = []
    if os.path.isdir(models_dir):
        names = os.listdir(models_dir)
        for name in names:
            path = os.path.join(models_dir, name)
            if os.path.isdir(path):
                model_path, model_type, obj = load_model_info(path, False)
                if model_path:
                    model = {
                        "name": os.path.splitext(os.path.basename(model_path))[0],
                        "path": os.path.abspath(model_path),
                        "model_type": model_type,
                        "is_dir": True
                    }
                    models.append(model)
            elif os.path.splitext(path)[1] == ".mud":
                model_path, model_type, obj = load_mud_model(path, False)
                if model_path:
                    model = {
                        "name": os.path.splitext(os.path.basename(model_path))[0],
                        "path": os.path.abspath(model_path),
                        "model_type": model_type,
                        "is_dir": False
                    }
                    models.append(model)
    return models

def remove_mud_model(mud_path):
    config = configparser.ConfigParser()
    config.read(mud_path)
    model_path = config.get("basic", "model", fallback=None)
    if not model_path:
        return
    model_path = os.path.join(os.path.dirname(mud_path), model_path)
    try:
        if os.path.exists(model_path):
            os.remove(model_path)
        os.remove(mud_path)
    except Exception as e:
        print("detele mud file failed:", e)

