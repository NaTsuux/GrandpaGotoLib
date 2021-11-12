import json
from enum import Enum


class Query(Enum):
    keep_alive_query = {
        "operationName": "getUserCancleConfig",
        "query": "query getUserCancleConfig {\n userAuth {\n user {\n holdValidate: getSchConfig(fields: \"hold_validate\", extra: true)\n }\n }\n}",
        "variables": {}
    }

    @staticmethod
    def do_keep_alive_query():
        return json.dumps(Query.keep_alive_query)


class PreserveQuery(Enum):
    pre_seat_status_query = {"operationName": "libLayout",
                             "query": "query libLayout($libId: Int!) {\n userAuth {\n prereserve {\n libLayout(libId: $libId) {\n max_x\n max_y\n seats_booking\n seats_total\n seats_used\n seats {\n key\n name\n seat_status\n status\n type\n x\n y\n }\n }\n }\n }\n}",
                             "variables": {"libId": 323}}

    check_msg_query = {"operationName": "prereserveCheckMsg",
                       "query": "query prereserveCheckMsg {\n userAuth {\n prereserve {\n prereserveCheckMsg\n }\n }\n}"}

    get_step_query = {"operationName": "getStep",
                      "query": "query getStep {\n userAuth {\n prereserve {\n getStep\n queeUrl\n successUrl\n endTime\n }\n }\n}"}

    get_captcha_query = {"operationName": "getStep0",
                         "query": "query getStep0 {\n userAuth {\n prereserve {\n getNum\n captcha {\n code\n data\n }\n }\n }\n}"}

    submit_captcha_query = {"operationName": "setStep1",
                            "query": "mutation setStep1($captcha: String!, $captchaCode: String!) {\n userAuth {\n prereserve {\n verifyCaptcha(captcha: $captcha, code: $captchaCode)\n setStep1\n }\n }\n}",
                            "variables": {"captcha": "", "captchaCode": ""}}

    pre_goto_step2_query = {"operationName": "setStep2",
                            "query": "mutation setStep2($token: String!) {\n userAuth {\n prereserve {\n setStep2(token: $token)\n }\n }\n}",
                            "variables": {
                                "token": "out=Oznf&sid=1219125&t=7fc30dd26185eea863368c018f31dd95&time=1631103011"}}

    do_pre_seat_query = {"operationName": "save",
                         "query": "mutation save($key: String!, $libid: Int!, $captchaCode: String, $captcha: String) {\n userAuth {\n prereserve {\n save(key: $key, libId: $libid, captcha: $captcha, captchaCode: $captchaCode)\n }\n }\n}",
                         "variables": {"key": "12,23", "libid": 323, "captchaCode": "", "captcha": ""}}

    preserve_status_query = {"operationName": "prereserve",
                             "query": "query prereserve {\n userAuth {\n prereserve {\n prereserve {\n day\n lib_id\n seat_key\n seat_name\n is_used\n user_mobile\n id\n lib_name\n }\n }\n }\n}"}

    pre_lib_status_query = {"operationName": "index",
                            "query": "query index {\n userAuth {\n user {\n prereserveAuto: getSchConfig(extra: true, fields: \"prereserve.auto\")\n }\n currentUser {\n sch {\n isShowCommon\n }\n }\n prereserve {\n libs {\n is_open\n lib_floor\n lib_group_id\n lib_id\n lib_name\n num\n seats_total\n }\n }\n oftenseat {\n prereserveList {\n id\n info\n lib_id\n seat_key\n status\n }\n }\n }\n}"}

    pickup_seat_status_query = {"operationName": "libLayout",
                                "query": "query libLayout($libId: Int!) {\n userAuth {\n prereserve {\n libLayout(libId: $libId) {\n max_x\n max_y\n seats_booking\n seats_total\n seats_used\n seats {\n key\n name\n seat_status\n status\n type\n x\n y\n }\n }\n }\n }\n}",
                                "variables": {"libId": 0}}

    @staticmethod
    def fill_pre_lib_status_query():
        return json.dumps(PreserveQuery.pre_lib_status_query.value)

    @staticmethod
    def fill_seat_status_query(lib_id: int):
        result = PreserveQuery.pickup_seat_status_query.value
        result.get("variables").update({"libId": lib_id})
        return json.dumps(result)

    @staticmethod
    def fill_do_take_seat_query(seat_key: str, lib_id: int):
        result = PreserveQuery.do_pre_seat_query.value
        result.get("variables").update({"key": seat_key, "libid": lib_id})
        return json.dumps(result)

    @staticmethod
    def fill_pre_goto_step2_query(token: str):
        result = PreserveQuery.pre_goto_step2_query.value
        result.get("variables").update({"token": token})
        return json.dumps(result)

    @staticmethod
    def fill_submit_captcha_query(captcha: str, captcha_code: str):
        result = PreserveQuery.submit_captcha_query.value
        result.get("variables").update({"captcha": captcha, "captchaCode": captcha_code})
        return json.dumps(result)

    @staticmethod
    def fill_check_msg_query():
        return json.dumps(PreserveQuery.check_msg_query.value)

    @staticmethod
    def fill_get_step_query():
        return json.dumps(PreserveQuery.get_step_query.value)

    @staticmethod
    def fill_get_captcha_query():
        return json.dumps(PreserveQuery.get_captcha_query.value)

    @staticmethod
    def fill_preserve_status_query():
        return json.dumps(PreserveQuery.preserve_status_query.value)


class ReserveQuery(Enum):
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

    @staticmethod
    def fill_lib_status_query():
        return json.dumps(ReserveQuery.reserve_lib_status_query.value)

    @staticmethod
    def fill_seat_status_query(lib_id: int):
        result = ReserveQuery.reserve_seat_status_query.value
        result.get("variables").update({"libId": lib_id})
        return json.dumps(result)

    @staticmethod
    def fill_do_reserve_seat_query(seat_key: str, lib_id: int):
        result = ReserveQuery.do_reserve_seat_query.value
        result.get("variables").update({"seatKey": seat_key})
        result.get("variables").update({"libId": lib_id})
        return json.dumps(result)


if __name__ == '__main__':
    print(type(PreserveQuery.get_captcha_query) is PreserveQuery)
