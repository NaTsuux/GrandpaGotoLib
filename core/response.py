import json


class Response:

    def __init__(self, response):
        self.response = response
        self.text = response.text
        self.json = json.loads(self.text)

    @property
    def status_code(self):
        return self.response.status_code

    @property
    def content(self):
        return self.response.content

    @property
    def general_status(self):
        return self.json.get("data").get("userAuth")


class PreserveResponse(Response):

    def __init__(self, response):
        super(PreserveResponse, self).__init__(response)

    @property
    def general_status(self):
        return super(PreserveResponse, self).general_status.get("prereserve")

    @property
    def preserve_check_msg(self):
        return self.general_status.get("prereserveCheckMsg")

    @property
    def step(self):
        return self.general_status.get("getStep")

    @property
    def success_url(self):
        return self.general_status.get("successUrl")

    @property
    def captcha_url(self):
        return self.general_status.get("captcha")

    @property
    def captcha_code(self):
        return self.general_status.get("code")

    @property
    def verified(self):
        return self.general_status.get("verifyCaptcha")

    @property
    def lib_statuses(self):
        return self.general_status.get("libs")

    @property
    def lib_layout(self):
        return self.general_status.get("libLayout")

    @property
    def saved(self):
        return self.general_status.get("save")


class ReserveResponse(Response):
    def __init__(self, response):
        super(ReserveResponse, self).__init__(response)
