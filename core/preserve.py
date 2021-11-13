import logging
import time

from .utils import calc_target_time, check_seat_privilege
from .querycontent import PreserveQuery
from .io import *
from .utils import LibLayout, Seat, log_response, LibStatus
from .queryapi import QueryApi
from .constant import PRESERVE_SESSION, SEAT_AVAILABLE_TYPE


class Preserve(QueryApi):

    def __init__(self):
        super(Preserve, self).__init__()
        self.session.set_type(PRESERVE_SESSION)
        self.logger = logging.getLogger("pre-reserve")

    def do_check_msg_query(self):
        return self.session.post(data=PreserveQuery.fill_check_msg_query())

    def do_check_preserve_status_query(self):
        return self.session.post(data=PreserveQuery.fill_preserve_status_query())

    def do_get_step_query(self):
        return self.session.post(data=PreserveQuery.fill_get_step_query())

    def do_get_captcha_query(self):
        return self.session.post(data=PreserveQuery.fill_get_captcha_query())

    def do_get_captcha_image(self, url):
        return self.session.get_pict(url=url)

    def do_submit_captcha_query(self, captcha_input, captcha_code):
        return self.session.post(
            PreserveQuery.fill_submit_captcha_query(captcha_input, captcha_code))

    def do_lib_status_query(self):
        return self.session.post(PreserveQuery.fill_pre_lib_status_query())

    def do_seat_status_query(self, lib_id: int):
        return self.session.post(PreserveQuery.fill_seat_status_query(lib_id))

    def do_take_seat_query(self, seat_key: str, lib_id: int):
        return self.session.post(PreserveQuery.fill_do_take_seat_query(seat_key, lib_id))

    def wait_timer(self):
        if self._timer is None:
            return
        target_time = calc_target_time(self._timer)
        while True:
            req = self.do_check_msg_query()
            self.logger.info(f"Timer: {req.general_status}")
            # TODO
            server_time = int(req.cookies.get("SERVERID").split('|')[1])

            now_time = int(time.time())
            self.logger.info(f"Timer: {server_time - now_time} seconds difference between server and local")

            if target_time - server_time <= 0:
                break

            sleep_time = min(target_time - server_time, 30)
            self.logger.info(f"Timer: {target_time - server_time} seconds to wait")
            self.logger.info(f"Timer: Sleep for {sleep_time} seconds")
            time.sleep(sleep_time)

    def run(self):
        self.wait_timer()

        while True:
            try:
                req = self.do_check_msg_query()
                if len(req.preserve_check_msg) != 0:
                    time.sleep(1)
                    continue

                # 测试一下
                req = self.do_take_seat_query("23,38", 324)
                log_response("test", req)

                # get_step返回中的getStep为0时是输入验证码之前，为1表示排队，为2表示可以选
                # 在8:10-8:13期间 第一次进去getStep会获取为0
                req = self.do_get_step_query()
                if self.log_level == 2:
                    log_response(req, "get_step")

                if req.step == 0:
                    # 这个url好像每次进入预约都是一样的? 不知道有什么用
                    target_url = req.success_url
                    # 获取验证码的图片url及code
                    captcha = self.do_get_captcha_query()
                    if self.log_level == 1:
                        write_file("pre_captcha_query.json", captcha.text)

                    img = self.do_get_captcha_image(captcha.captcha_url)
                    write_file("captcha.jpg", img.content)

                    # 提交验证码 请求体中是setStep1
                    while True:
                        captcha_input = input()
                        req = self.do_submit_captcha_query(captcha_input, captcha.captcha_code)
                        if self.log_level == 1:
                            write_file("pre_captcha_submit_query.json", req.text)
                        if req.verified:
                            break
                        else:
                            self.logger.warning("Wrong Captcha Code")

                # # 验证码正确
                # # setStep1=wss://wechat.v2.traceint.com/quee/quee?sid=1219125&schId=93&in=tSWg&time=1631103006&t=5643b316258b0b3f71095a0f58ee42fe
                # # 排队的时候转换成了websocket?
                # web_socket_header = {
                #     "Sec-WebSocket-Extensions": "permessage-deflate; client_max_window_bits",
                #     "Sec-WebSocket-Version": 13,
                #     "Sec-WebSocket-Key": "BLHYQqoWWx3MqD2J6M9Sww=="
                # }
                # set_step1 = get_general_status(req.text).get("prereserve").get("setStep1").replace("wss://", "https://")
                # # 用step1的地址排队？请求体中有不知道怎么来的token 可能是在websocket通信期间获取的
                # # TODO websocket
                #
                # token = "Something"
                # # 请求体中setStep2
                # req = session.post(url=url, data=fill_pre_goto_step2_query(token))
                # set_step2 = get_general_status(req.text).get("prereserve").get("setStep2")
                # # 有没有可能不用排队这部分？

                while True:
                    req = self.do_lib_status_query()

                    lib_status = req.lib_statuses
                    free_seat = []
                    # for lib in lib_status:
                    #     if int(lib.get("num")) != 0 and int(lib.get("")):
                    #         free_seat.append(lib)

                    # for lib in free_seat:
                    lib_id = 324
                    result = self.do_seat_status_query(lib_id)
                    if self.log_level == 1:
                        log_response(result, f"seat_map_{lib_id}")

                    lib_layout = LibLayout(result.lib_layout)
                    seat_list: list = lib_layout.seats

                    available_seat_list = []
                    for seat in seat_list:
                        # 这里很关键 可以重构一下扩展性
                        if seat.get('type') == SEAT_AVAILABLE_TYPE and not seat.get('status') \
                                and check_seat_privilege(lib_id, seat.get('name')):
                            available_seat_list.append(Seat(seat))
                    self.logger.info(f"Available seat list: {available_seat_list}")

                    for seat in available_seat_list:
                        # 发送保留座位请求
                        req = self.do_take_seat_query(seat.key, lib_id)
                        if req.saved:
                            self.logger.info("Pre-reserve success!")
                            req = self.do_check_preserve_status_query()
                            self.logger.info(req.general_status)
                        time.sleep(0.5)
                        return

            except AttributeError:
                self.logger.error("Error occurred QAQ")
                continue

    def pickup(self):
        self.wait_timer()
        count = 0

        while True:
            count += 1
            req = self.do_lib_status_query()
            if self.log_level == 1:
                log_response(req, "pre_pickup_lib_status")

            lib_status = [LibStatus(lib) for lib in req.lib_statuses]
            free_seat = list(filter(None, [lib if lib.has_free_seat else None for lib in lib_status]))

            # 现在是否有空余座位
            if len(free_seat) == 0:
                self.logger.info(f"No seat available in request #{count}")
            else:
                self.logger.info(f"Seat available in {[i.lib_name for i in free_seat]}")

            # 对A区或B区的空余预定座位进行一个捡漏
            for lib in free_seat:
                lib_id = lib.lib_id
                result = self.do_seat_status_query(lib_id)

                if self.log_level == 1:
                    log_response(result, f"pre_seat_status_{lib_id}")

                lib_layout = LibLayout(result.lib_layout)
                seat_list: dict = lib_layout.seats

                available_seat_list = []
                for seat in seat_list:
                    # 这里很关键 可以重构一下扩展性
                    if seat.get('type') == SEAT_AVAILABLE_TYPE and not seat.get('status') \
                            and check_seat_privilege(lib_id, seat.get('name')):
                        available_seat_list.append(Seat(seat))
                self.logger.info(f"Available seat list: {available_seat_list}")

                for seat in available_seat_list:
                    req = self.do_take_seat_query(seat.key, lib_id)
                    if req.seat_reserved:
                        self.logger.info(
                            f"Pickup success! {lib.lib_name} No.{available_seat_list[0].name}")
                    exit(0)

            self.logger.info("========================================")
            time.sleep(self.config.delay)


preserve = Preserve()
