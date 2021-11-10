import _io
import json
import os

pre_seat_status_query = {"operationName": "libLayout",
                         "query": "query libLayout($libId: Int!) {\n userAuth {\n prereserve {\n libLayout(libId: $libId) {\n max_x\n max_y\n seats_booking\n seats_total\n seats_used\n seats {\n key\n name\n seat_status\n status\n type\n x\n y\n }\n }\n }\n }\n}",
                         "variables": {"libId": 323}}

pre_check_msg_query = {"operationName": "prereserveCheckMsg",
                       "query": "query prereserveCheckMsg {\n userAuth {\n prereserve {\n prereserveCheckMsg\n }\n }\n}"}

pre_get_step_query = {"operationName": "getStep",
                      "query": "query getStep {\n userAuth {\n prereserve {\n getStep\n queeUrl\n successUrl\n endTime\n }\n }\n}"}

pre_get_captcha_query = {"operationName": "getStep0",
                         "query": "query getStep0 {\n userAuth {\n prereserve {\n getNum\n captcha {\n code\n data\n }\n }\n }\n}"}

pre_submit_captcha_query = {"operationName": "setStep1",
                            "query": "mutation setStep1($captcha: String!, $captchaCode: String!) {\n userAuth {\n prereserve {\n verifyCaptcha(captcha: $captcha, code: $captchaCode)\n setStep1\n }\n }\n}",
                            "variables": {"captcha": "", "captchaCode": ""}}

pre_goto_step2_query = {"operationName": "setStep2",
                        "query": "mutation setStep2($token: String!) {\n userAuth {\n prereserve {\n setStep2(token: $token)\n }\n }\n}",
                        "variables": {
                            "token": "out=Oznf&sid=1219125&t=7fc30dd26185eea863368c018f31dd95&time=1631103011"}}

do_pre_seat_query = {"operationName": "save",
                     "query": "mutation save($key: String!, $libid: Int!, $captchaCode: String, $captcha: String) {\n userAuth {\n prereserve {\n save(key: $key, libId: $libid, captcha: $captcha, captchaCode: $captchaCode)\n }\n }\n}",
                     "variables": {"key": "12,23", "libid": 323, "captchaCode": "", "captcha": ""}}

pre_status_query = {"operationName": "prereserve",
                    "query": "query prereserve {\n userAuth {\n prereserve {\n prereserve {\n day\n lib_id\n seat_key\n seat_name\n is_used\n user_mobile\n id\n lib_name\n }\n }\n }\n}"}


def fill_do_pre_seat_query(seat_key: str, lib_id: int):
    result = do_pre_seat_query.copy()
    result.get("variables").update({"key": seat_key, "libid": lib_id})
    return json.dumps(result)


def fill_pre_goto_step2_query(token: str):
    result = pre_goto_step2_query.copy()
    result.get("variables").update({"token": token})
    return json.dumps(result)


def fill_pre_submit_captcha_query(captcha: str, captcha_code: str):
    result = pre_submit_captcha_query.copy()
    result.get("variables").update({"captcha": captcha, "captchaCode": captcha_code})
    return json.dumps(result)


reserve_lib_status_query = {"operationName": "list",
                            "query": "query list {\n userAuth {\n reserve {\n libs(libType: -1) {\n lib_id\n lib_floor\n is_open\n lib_name\n lib_type\n lib_group_id\n lib_comment\n lib_rt {\n seats_total\n seats_used\n seats_booking\n seats_has\n reserve_ttl\n open_time\n open_time_str\n close_time\n close_time_str\n advance_booking\n }\n }\n libGroups {\n id\n group_name\n }\n reserve {\n isRecordUser\n }\n }\n record {\n libs {\n lib_id\n lib_floor\n is_open\n lib_name\n lib_type\n lib_group_id\n lib_comment\n lib_color_name\n lib_rt {\n seats_total\n seats_used\n seats_booking\n seats_has\n reserve_ttl\n open_time\n open_time_str\n close_time\n close_time_str\n advance_booking\n }\n }\n }\n rule {\n signRule\n }\n }\n}"}

reserve_seat_status_query = {"operationName": "libLayout",
                             "query": "query libLayout($libId: Int, $libType: Int) {\n userAuth {\n reserve {\n libs(libType: $libType, libId: $libId) {\n lib_id\n is_open\n lib_floor\n lib_name\n lib_type\n lib_layout {\n seats_total\n seats_booking\n seats_used\n max_x\n max_y\n seats {\n x\n y\n key\n type\n name\n seat_status\n status\n }\n }\n }\n }\n }\n}",
                             "variables": {"libId": 0}}

do_reserve_seat_query = {
    "operationName": "reserveSeat",
    "query": "mutation reserveSeat($libId: Int!, $seatKey: String!, $captchaCode: String, $captcha: String!) {\n userAuth {\n reserve {\n reserveSeat(\n libId: $libId\n seatKey: $seatKey\n captchaCode: $captchaCode\n captcha: $captcha\n )\n }\n }\n}",
    "variables": {
        "seatKey": "",
        "libId": 0,
        "captchaCode": "",
        "captcha": ""
    }
}


def fill_reserve_lib_status_query_attr():
    return json.dumps(reserve_lib_status_query)


def fill_reserve_seat_status_query_attr(lib_id: int):
    result = reserve_seat_status_query.copy()
    result.get("variables").update({"libId": lib_id})
    return json.dumps(result)


def fill_do_reserve_seat_query_attr(seat_key: str, lib_id: int):
    result = do_reserve_seat_query.copy()
    result.get("variables").update({"seatKey": seat_key})
    result.get("variables").update({"libId": lib_id})
    return json.dumps(result)


host = "https://wechat.v2.traceint.com"

url = "https://wechat.v2.traceint.com/index.php/graphql/"

header = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63030068)",
    "Connection": "keep-alive",
    "Host": "wechat.v2.traceint.com",
    "Content-Type": "application/json",
    "Referer": "https://web.traceint.com/web/index.html",
    "Sec-Fetch-Site": "same-site",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty"
}


def read_file(file_name: str):
    return open(os.path.join("data", file_name), 'r').read()


def write_file(file_name: str, data: str):
    with open(os.path.join("data", file_name), "w") as f:
        f.write(data)
    f.close()


def get_general_status(data):
    try:
        if isinstance(data, str):
            return json.loads(data).get("data").get("userAuth")
        elif isinstance(data, _io.TextIOWrapper):
            return json.load(open("data/seat_status.json")).get("data").get("userAuth")
    except AttributeError:
        pass


def get_lib_layout(data):
    if isinstance(data, str):
        return json.loads(data).get("data").get("userAuth").get("reserve").get("libs")[0].get('lib_layout')
    elif isinstance(data, _io.TextIOWrapper):
        return json.load(open("data/seat_status.json")).get("data").get("userAuth").get("reserve").get("libs")[0].get(
            'lib_layout')
