import datetime
import json
import time

from .constant import STATIC_PATH
from .io import read_file, write_file
from requests.cookies import cookiejar_from_dict


def get_cookie_jar():
    cookie = read_file("cookie.txt", STATIC_PATH)
    cookie_json = {}
    for line in cookie.split(";"):
        if line.find("=") != -1:
            name, value = line.strip().split("=")
            cookie_json[name] = value
    cookies = cookiejar_from_dict(cookie_json)
    return cookies


def get_header_dict():
    headers = read_file("headers.json", STATIC_PATH)
    return json.loads(headers)


def calc_target_time(target: str):
    now_time = datetime.datetime.now()
    target_time = now_time.strftime("%Y-%m-%d") + f" {target}"
    time_array = time.strptime(target_time, "%Y-%m-%d %H:%M:%S")
    target_stamp = time.mktime(time_array)
    if time.time() > target_stamp:
        target_stamp += 86400
    return target_stamp


def log_response(response, func_name=None):
    file_name = datetime.datetime.now().strftime('%H-%M-%S')
    if func_name:
        file_name += f"_{func_name}"
    file_name += ".json"
    write_file(file_name, response.text)


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


class LibStatus:
    # lib_id: int
    # lib_floor: str
    # is_open: bool
    # lib_name: str
    # lib_type: int
    # lib_group_id: int
    # lib_comment: str
    # lib_rt: LibRt

    def __init__(self, lib_status):
        self.lib_id = int(lib_status.get("lib_id"))
        self.lib_floor = lib_status.get("lib_floor")
        self.is_open = lib_status.get("is_open")
        self.lib_name = lib_status.get("lib_name")
        self.lib_type = lib_status.get("lib_type")
        self.lib_group_id = int(lib_status.get("lib_group_id"))
        self.lib_comment = lib_status.get("lib_comment")
        self.lib_rt = None if lib_status.get("lib_rt") is None else LibRt(lib_status.get("lib_rt"))
        self.num = None if lib_status.get("num") is None else int(lib_status.get("num"))

    @property
    def has_free_seat(self):
        return self.lib_rt.seats_has != 0 if self.num is None else self.num != 0


class LibRt:
    seats_total: int
    seats_used: int
    seats_booking: int
    seats_has: int
    reserve_ttl: int
    open_time: int
    open_time_str: str
    close_time: str
    close_time_str: str
    advance_booking: str

    def __init__(self, lib_rt):
        self.__dict__.update(lib_rt)


def check_seat_privilege(lib_id: int, seat_name: str):
    if lib_id == 324 and seat_name in ["001", "002", "003", "004", "005", "006", "007", "008", "009",
                                       "010", "011", "012"]:
                                       # "108", "109", "110", "111", "112", "113",
                                       # "114", "115", "116", "117", "118", "119", "120", "121", "122",
                                       # "123", "124", "125", "126", "127", "128", "129", "130", "131"]:
        return False
    elif lib_id == 323:
        return False
    return True
