from .io import open_file
from .constant import STATIC_PATH
import yaml


class Config:

    def __init__(self):
        config = yaml.load(open_file("config.yml", "r", location=STATIC_PATH, encoding="utf-8"), Loader=yaml.CLoader)
        self.__dict__.update(config)
