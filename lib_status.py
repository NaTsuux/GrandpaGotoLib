import json
from dataclasses import dataclass

SEAT_AVAILABLE_CODE = 1


# @dataclass
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
    type: int
    name: str
    seat_status: int
    status: bool

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
        self.lib_type = int(lib_status.get("lib_type"))
        self.lib_group_id = int(lib_status.get("lib_group_id"))
        self.lib_comment = lib_status.get("lib_comment")
        self.lib_rt = LibRt(lib_status.get("lib_rt"))

    def has_free_seat(self):
        return self.lib_rt.seats_has != 0


class ReserveList:
    # libs: [LibStatus]
    # libGroups: []
    # reserve: bool

    def __init__(self, reserve):
        self.libs = []
        for lib in reserve.get("libs"):
            self.libs.append(LibStatus(lib))
        self.libGroups = reserve.get("libGroups")
        self.reserve = reserve.get("reserve")

    def get_lib_id_with_free_seat(self):
        result = []
        for lib in self.libs:
            if lib.has_free_seat():
                result.append(lib.lib_id)
        return result


class UserAuth:
    # reserve: ReserveList
    # record: dict
    # rule: dict

    def __init__(self, user_auth_dict):
        self.reserve: ReserveList = ReserveList(user_auth_dict.get("reserve"))
        self.record = user_auth_dict.get("record")
        self.rule = user_auth_dict.get("rule")

    def get_reserve_attr(self):
        return self.reserve.reserve

    def get_lib_list(self):
        return self.reserve.libs

    def get_lib_id_with_free_seat(self):
        return self.reserve.get_lib_id_with_free_seat()

    def get_lib_name_by_id(self, lib_id):
        for lib in self.reserve.libs:
            if lib.lib_id == lib_id:
                return lib.lib_name
