import logging
import time

import utils
from .querycontent import Preserve
from .session import session
from .io import *
from .utils import LibLayout, Seat

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("pre-reserve")
session = session()


def wait_timer():
    target_time = utils.calc_target_time()
    while True:
        req = session.post(data=Preserve.fill_check_msg_query())
        logger.info(f"Timer: {req.general_status}")
        server_time = int(req.cookies.get("SERVERID").split('|')[1])

        now_time = int(time.time())
        logger.info(f"Timer: {server_time - now_time} seconds difference between server and local")

        if target_time - server_time <= 0:
            break

        sleep_time = min(target_time - server_time, 30)
        logger.info(f"Timer: {target_time - server_time} seconds to wait")
        logger.info(f"Timer: Sleep for {sleep_time} seconds")
        time.sleep(sleep_time)


def preserve():
    wait_timer()

    while True:
        try:
            req = session.post(data=Preserve.check_msg_query)
            if len(req.preserve_check_msg) != 0:
                time.sleep(1)
                continue

            # get_step返回中的getStep为0时是输入验证码之前，为1表示排队，为2表示可以选
            # 在8:10-8:13期间 第一次进去getStep会获取为0
            req = session.post(data=Preserve.fill_get_step_query())
            write_file("pre_get_step_query.json", req.text)

            if req.step == 0:
                # 这个url好像每次进入预约都是一样的? 不知道有什么用
                target_url = req.success_url
                # 获取验证码的图片url及code
                captcha = session.post(data=Preserve.get_captcha_query)
                write_file("pre_captcha_query.json", captcha.text)

                img = session.get_pict(url=captcha.captcha_url)
                write_file("captcha.jpg", img.content)

                # 提交验证码 请求体中是setStep1
                while True:
                    captcha_input = input()
                    req = session.post(data=Preserve.fill_submit_captcha_query(captcha_input, captcha.captcha_code))
                    write_file("pre_captcha_submit_query.json", req.text)
                    if req.verified:
                        break
                    else:
                        logger.warning("Wrong Captcha Code")

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
                req = session.post(Preserve.fill_pre_lib_status_query())

                lib_status = req.lib_statuses
                free_seat = []
                # for lib in lib_status:
                #     if int(lib.get("num")) != 0 and int(lib.get("")):
                #         free_seat.append(lib)

                # for lib in free_seat:
                lib_id = 324
                result = session.post(Preserve.fill_seat_status_query(lib_id))
                write_file("pre_seat_map.json", result.text)

                lib_layout = LibLayout(result.lib_layout)
                seat_list: dict = lib_layout.seats

                available_seat_list = []
                for seat in seat_list:
                    # 这里很关键 可以重构一下扩展性
                    if seat.get('type') == constant.SEAT_AVAILABLE_TYPE and not seat.get('status') \
                            and utils.check_seat_privilege(lib_id, seat.get('name')):
                        available_seat_list.append(Seat(seat))
                logger.info(f"Available seat list: {available_seat_list}")

                for seat in available_seat_list:
                    # 发送保留座位请求
                    req = session.post(Preserve.fill_do_take_seat_query(seat.key, lib_id))
                    if req.saved:
                        logger.info("Pre-reserve success!")
                        req = session.post(Preserve.fill_preserve_status_query())
                        logger.info(req.general_status)
                        return

        except AttributeError:
            logger.error("Error occurred QAQ")
            continue
