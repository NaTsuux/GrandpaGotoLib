import datetime
import time
import json
from stuffs import *

from requests.cookies import cookiejar_from_dict

import yaml
from lib_status import *
import requests
import logging
# import matplotlib.pyplot as plt

cookie = read_file("cookie.txt")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
basic_logger = logging.getLogger(__name__)
pickup_logger = logging.getLogger("pickup")
pre_logger = logging.getLogger("pre")

config = yaml.load(open("data/config.yml", "r", encoding="utf-8"), Loader=yaml.CLoader)

basic_logger.info(config)

session = requests.session()


def get_cookie_jar():
    cookie_json = {}
    for line in cookie.split(";"):
        if line.find("=") != -1:
            name, value = line.strip().split("=")
            cookie_json[name] = value
    cookies = cookiejar_from_dict(cookie_json)
    return cookies


def check_seat_privilege(lib_id: int, seat_name: str):
    if lib_id == 324 and seat_name in ["001", "002", "003", "004", "005", "006", "007", "008", "009",
                                       "010", "011", "012", "108", "109", "110", "111", "112", "113",
                                       "114", "115", "116", "117", "118", "119", "120", "121", "122",
                                       "123", "124", "125", "126", "127", "128", "129", "130", "131"]:
        return False
    elif lib_id == 323:
        return False
    return True


def pickup():
    count = 0

    while True:
        count += 1

        basic_logger.info(f"Sending request #{count}")
        req = session.post(url=url, data=fill_reserve_lib_status_query())
        # req = session.post(url=url, data=reserve_seat_status_query)
        basic_logger.info(f"Status code: {req.status_code}, Response body length: {len(req.text)}")
        write_file("seat_status.json", req.text)

        general_status: dict = get_general_status(req.text)

        lib_status = UserAuth(general_status)
        free_seat = lib_status.get_lib_id_with_free_seat()

        # 现在是否有空余座位
        if len(free_seat) == 0:
            basic_logger.info(f"No seat available in request #{count}")
        else:
            basic_logger.info(f"Seat available in {[lib_status.get_lib_name_by_id(i) for i in free_seat]}")

        # 对A区或B区的空余座位进行一个捡漏
        for lib_id in free_seat:
            if lib_id == 323:
                continue
            result = session.post(url=url, data=fill_reserve_seat_status_query(lib_id))
            write_file("seat_map.json", result.text)

            lib_layout = LibLayout(get_lib_layout(result.text))
            seat_list: dict = lib_layout.seats

            available_seat_list = []
            for seat in seat_list:
                if seat.get('seat_status') == SEAT_AVAILABLE_STATUS and check_seat_privilege(lib_id, seat.get('name')):
                    available_seat_list.append(Seat(seat))
            pickup_logger.info(f"Available seat list: {available_seat_list}")

            # 获取到空余座位的seat key
            if len(available_seat_list) != 0:
                req = session.post(url=url, data=fill_do_reserve_seat_query(available_seat_list[0].key, lib_id))
                reserve_seat_result = get_general_status(req.text).get("reserve").get("reserveSeat")
                if reserve_seat_result:
                    pickup_logger.info(
                        f"Pickup success! {lib_status.get_lib_name_by_id(lib_id)} No.{available_seat_list[0].name}")
                exit(0)

        basic_logger.info("========================================")

        time.sleep(config.get('delay'))


def pre_pickup():
    count = 0

    while True:
        count += 1
        req = session.post(url=url, data=fill_pre_pickup_lib_status_query())
        pickup_logger.info(f"Status code: {req.status_code}, Response body length: {len(req.text)}")
        write_file("seat_status.json", req.text)

        general_status: dict = get_general_status(req.text)

        lib_status = general_status.get("prereserve").get("libs")
        free_seat = []
        for lib in lib_status:
            if int(lib.get("num")) != 0:
                free_seat.append(lib)

        # 现在是否有空余座位
        if len(free_seat) == 0:
            pickup_logger.info(f"No seat available in request #{count}")
        else:
            pickup_logger.info(f"Seat available in {[i.get('lib_name') for i in free_seat]}")

        # 对A区或B区的空余预定座位进行一个捡漏
        for lib in free_seat:
            lib_id = lib.get("lib_id")
            result = session.post(url=url, data=fill_pre_pickup_seat_status_query(lib_id))
            write_file("seat_map.json", result.text)

            lib_layout = LibLayout(get_general_status(result.text).get("prereserve").get("libLayout"))
            seat_list: dict = lib_layout.seats

            available_seat_list = []
            for seat in seat_list:
                # 这里很关键 可以重构一下扩展性
                if seat.get('type') == SEAT_AVAILABLE_TYPE and not seat.get('status') \
                        and check_seat_privilege(lib_id, seat.get('name')):
                    available_seat_list.append(Seat(seat))
            pickup_logger.info(f"Available seat list: {available_seat_list}")

            if len(available_seat_list) != 0:
                req = session.post(url=url, data=fill_do_pre_seat_query(available_seat_list[0].key, lib_id))
                save = get_general_status(req.text).get("prereserve").get("save")
                if save:
                    pickup_logger.info(
                        f"Pickup success! {lib_id} No.{available_seat_list[0].name}")
                exit(0)

        basic_logger.info("========================================")
        time.sleep(config.get('delay'))


def calc_target_time():
    now_time = datetime.datetime.now()
    target_time = now_time.strftime("%Y-%m-%d") + " 20:09:58"
    time_array = time.strptime(target_time, "%Y-%m-%d %H:%M:%S")
    return time.mktime(time_array)


def pre_reserve():
    target_time = calc_target_time()

    while True:
        req = session.post(url=url, data=json.dumps(pre_check_msg_query))
        pre_logger.info(f"{get_general_status(req.text).get('prereserve')}")
        server_time = int(req.cookies.get("SERVERID").split('|')[1])

        now_time = int(time.time())
        pre_logger.info(f"{server_time - now_time} seconds difference between server and local")

        if target_time - server_time <= 0:
            break

        sleep_time = min(target_time - server_time, 30)
        pre_logger.info(f"{target_time - server_time} seconds to wait")
        pre_logger.info(f"Sleep for {sleep_time} seconds")
        time.sleep(sleep_time)

    while True:
        try:
            req = session.post(url=url, data=json.dumps(pre_check_msg_query))
            if len(json.loads(req.text).get("data").get("userAuth").get("prereserve").get("prereserveCheckMsg")) != 0:
                time.sleep(1)
                continue

            # get_step返回中的getStep为0时是输入验证码之前，为1表示排队，为2表示可以选
            # 在8:10-8:13期间 第一次进去getStep会获取为0
            req = session.post(url=url, data=json.dumps(pre_get_step_query))
            write_file("pre_get_step_query.json", req.text)

            if get_general_status(req.text).get("prereserve").get("getStep") == 0:
                # 这个url好像每次进入预约都是一样的? 不知道有什么用
                target_url = str(json.loads(req.text).get("data").get("userAuth").get("prereserve").get("successUrl"))
                # 获取验证码的图片
                req = session.post(url=url, data=json.dumps(pre_get_captcha_query))
                write_file("pre_captcha_query.json", req.text)
                captcha = json.loads(req.text).get("data").get("userAuth").get("prereserve").get("captcha")

                session.headers.update({
                    "Sec-Fetch-Site": "same-site",
                    "Sec-Fetch-Mode": "no-cors",
                    "Sec-Fetch-Dest": "image"
                })
                img = requests.get(url=captcha.get("data"))
                session.headers.update({
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Dest": "empty"
                })
                # 上面的大概确实需要用到
                with open("a.jpg", "wb") as f:
                    f.write(img.content)
                f.close()
                # plt.imread("a.jpg")
                # plt.show()

                # 提交验证码 请求体中是setStep1
                while True:
                    captcha_input = input()
                    req = session.post(url=url, data=fill_pre_submit_captcha_query(captcha_input, captcha.get("code")))
                    write_file("pre_captcha_submit_query.json", req.text)
                    if get_general_status(req.text).get("prereserve").get("verifyCaptcha"):
                        break
                    else:
                        pre_logger.warning("Wrong Captcha Code")

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
                general_status: dict = get_general_status(req.text)

                lib_status = general_status.get("prereserve").get("libs")
                free_seat = []
                # for lib in lib_status:
                #     if int(lib.get("num")) != 0 and int(lib.get("")):
                #         free_seat.append(lib)

                # for lib in free_seat:
                lib_id = 324
                result = session.post(url=url, data=fill_pre_pickup_seat_status_query(lib_id))
                write_file("pre_seat_map.json", result.text)

                lib_layout = LibLayout(get_general_status(result.text).get("prereserve").get("libLayout"))
                seat_list: dict = lib_layout.seats

                available_seat_list = []
                for seat in seat_list:
                    # 这里很关键 可以重构一下扩展性
                    if seat.get('type') == SEAT_AVAILABLE_TYPE and not seat.get('status') \
                            and check_seat_privilege(lib_id, seat.get('name')):
                        available_seat_list.append(Seat(seat))
                pre_logger.info(f"Available seat list: {available_seat_list}")

                for seat in available_seat_list:
                    # 发送保留座位请求
                    req = session.post(url=url, data=fill_do_pre_seat_query(seat.key, lib_id))
                    save = get_general_status(req.text).get("prereserve").get("save")
                    if save:
                        pre_logger.info("Pre-reserve success!")
                        req = session.post(url=url, data=json.dumps(pre_status_query))
                        pre_logger.info(get_general_status(req.text))
                        return

        except AttributeError:
            pre_logger.error("Error occurred QAQ")
            continue


def test():
    # req = session.post(url=url, data=json.dumps(pre_get_captcha_query))
    # write_file("pre_captcha_query.json", req.text)
    # captcha = json.loads(req.text).get("data").get("userAuth").get("prereserve").get("captcha")

    session.headers.update({
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Dest": "image"
    })
    img = session.get(
        url="https://static.wechat.v2.traceint.com/template/theme2/cache/yzm/64b40877ad5339bcbff40855c0b47f62.jpg")
    session.headers.update({
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty"
    })
    # 上面的大概确实需要用到
    with open("a.jpg", "wb") as f:
        f.write(img.content)
    f.close()


if __name__ == "__main__":
    basic_logger.info("Program start")
    session.cookies = get_cookie_jar()
    session.headers = header

    basic_logger.info(f"Query delay {config.get('delay')}s")
    # pickup()
    # pre_reserve()
    pre_pickup()
    # test()
