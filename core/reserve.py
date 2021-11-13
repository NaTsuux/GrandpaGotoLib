import logging
import time

from core.queryapi import QueryApi
from core.querycontent import ReserveQuery
from .utils import log_response, LibLayout, check_seat_privilege, Seat, calc_target_time
from .constant import SEAT_AVAILABLE_STATUS
from .constant import RESERVE_SESSION


class Reserve(QueryApi):
    def __init__(self):
        super(Reserve, self).__init__()
        self.session.set_type(RESERVE_SESSION)
        self.logger = logging.getLogger("Reserve")

    def do_lib_status_query(self):
        return self.session.post(data=ReserveQuery.fill_lib_status_query())

    def do_seat_status_query(self, lib_id: int):
        return self.session.post(data=ReserveQuery.fill_seat_status_query(lib_id))

    def do_take_seat_query(self, seat_key, lib_id: int):
        return self.session.post(data=ReserveQuery.fill_do_reserve_seat_query(seat_key, lib_id))

    def wait_timer(self):
        if self._timer is None:
            return
        target_time = calc_target_time(self._timer)
        while True:
            req = self.do_keep_alive_query()
            self.logger.info(f"Timer: {req.general_status}")
            server_time = int(req.cookies.get("SERVERID").split('|')[1])

            now_time = int(time.time())
            self.logger.info(f"Timer: {server_time - now_time} seconds difference between server and local")

            if target_time - server_time <= 0:
                break

            sleep_time = min(target_time - server_time, 30)
            self.logger.info(f"Timer: {target_time - server_time} seconds to wait")
            self.logger.info(f"Timer: Sleep for {sleep_time} seconds")
            time.sleep(sleep_time)

    def pickup(self):
        count = 0
        self.wait_timer()

        while True:
            count += 1

            self.logger.info(f"Sending request #{count}")
            req = self.do_lib_status_query()
            log_response(req, "res_lib_status")

            lib_status = req.lib_statuses
            free_seat = list(filter(None, [lib if lib.has_free_seat else None for lib in lib_status]))

            # 现在是否有空余座位
            if len(free_seat) == 0:
                self.logger.info(f"No seat available in request #{count}")
            else:
                self.logger.info(f"Seat available in {[lib.lib_name for lib in free_seat]}")

            # 对A区或B区的空余座位进行一个捡漏
            for lib in free_seat:
                if lib.lib_id == 323:
                    continue
                lib_id = lib.lib_id
                result = self.do_seat_status_query(lib_id)
                if self.log_level >= 1:
                    log_response(result, f"res_seat_status_{lib_id}")

                lib_layout = LibLayout(result.lib_layout)
                seat_list: dict = lib_layout.seats

                available_seat_list = []
                for seat in seat_list:
                    if seat.get('seat_status') == SEAT_AVAILABLE_STATUS \
                            and check_seat_privilege(lib_id, seat.get('name')):
                        available_seat_list.append(Seat(seat))
                self.logger.info(f"Available seat list: {available_seat_list}")

                # 获取到空余座位的seat key
                for seat in available_seat_list:
                    req = self.do_take_seat_query(seat.key, lib_id)
                    if req.seat_reserved:
                        self.logger.info(
                            f"Pickup success! {lib.lib_name} No.{available_seat_list[0].name}")
                        exit(0)
                    else:
                        self.logger.warning(f"Something wrong occurred: {req.error_msg}")

            self.logger.info("========================================")

            time.sleep(self.config.delay)


reserve = Reserve()
