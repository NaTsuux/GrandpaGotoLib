import datetime
import json
import time

import constant
from .io import read_file
from requests.cookies import cookiejar_from_dict


def get_cookie_jar():
    cookie = read_file("cookie.txt", constant.STATIC_PATH)
    cookie_json = {}
    for line in cookie.split(";"):
        if line.find("=") != -1:
            name, value = line.strip().split("=")
            cookie_json[name] = value
    cookies = cookiejar_from_dict(cookie_json)
    return cookies


def get_header_dict():
    headers = read_file("headers.json", constant.STATIC_PATH)
    return json.loads(headers)


def calc_target_time():
    now_time = datetime.datetime.now()
    target_time = now_time.strftime("%Y-%m-%d") + " 20:09:58"
    time_array = time.strptime(target_time, "%Y-%m-%d %H:%M:%S")
    return time.mktime(time_array)


class LibLayout:
    max_x: int
    max_y: int
    seats: []

    def __init__(self, lib_layout):
        self.__dict__.update(lib_layout)


class Seat:
    x: int
    y: int
    key: str
    type: int  # 在pre时 5表示被锁 1表示可选
    name: str
    seat_status: int
    status: bool  # 在pre时 为true是可选

    def __init__(self, seat):
        self.__dict__.update(seat)

    def __repr__(self):
        return f"#{self.name}({self.x}, {self.y})"


def check_seat_privilege(lib_id: int, seat_name: str):
    if lib_id == 324 and seat_name in ["001", "002", "003", "004", "005", "006", "007", "008", "009",
                                       "010", "011", "012", "108", "109", "110", "111", "112", "113",
                                       "114", "115", "116", "117", "118", "119", "120", "121", "122",
                                       "123", "124", "125", "126", "127", "128", "129", "130", "131"]:
        return False
    elif lib_id == 323:
        return False
    return True
