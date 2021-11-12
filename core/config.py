from .io import open_file
import constant
import yaml


class Config:

    def __init__(self):
        config = yaml.load(open_file("config.yaml", constant.STATIC_PATH), Loader=yaml.CLoader)
        self.__dict__.update(config)
