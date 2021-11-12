import os
import constant

base = os.getcwd()
data_path = os.path.join(base, "data")
runtime_data_path = os.path.join(data_path, "run_time")
static_data_path = os.path.join(data_path, "static")


def open_file(file_name: str,
              method: str,
              location: int = constant.RUNTIME_PATH,
              encoding=None):

    if location == constant.STATIC_PATH:
        target_file = os.path.join(static_data_path, file_name)
    elif location == constant.RUNTIME_PATH:
        target_file = os.path.join(runtime_data_path, file_name)
    else:
        raise IOError

    if encoding is None:
        f = open(target_file, method)
    else:
        f = open(target_file, method, encoding=encoding)
    return f


def read_file(file_name: str,
              location: int = constant.RUNTIME_PATH,
              encoding=None):
    return open_file(file_name, "r", location, encoding).read()


def write_file(file_name: str,
               data,
               location: int = constant.RUNTIME_PATH,
               encoding=None):
    if file_name.split(".")[-1] in ["jpg", "png"]:
        f = open_file(file_name, "wb", location)
    else:
        f = open_file(file_name, "w", location, encoding)

    f.write(data)
