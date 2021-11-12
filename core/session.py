import requests
from .utils import get_cookie_jar
from .utils import get_header_dict
from .response import PreserveResponse, ReserveResponse, Response
from .constant import PRESERVE_SESSION, RESERVE_SESSION


class Session:

    def __init__(self):
        self.session = requests.session()
        self.session.cookies = get_cookie_jar()
        self.session.headers = get_header_dict()
        self.url = "https://wechat.v2.traceint.com/index.php/graphql/"
        self.type = None

    def set_type(self, session_type):
        self.type = session_type

    def post(self, data="", url=None):
        if url is None:
            url = self.url
        response = self.session.post(url=url, data=data)

        return self._type_based_return(response)

    def get(self, url=None, data=None):
        if url is None:
            url = self.url

        if data is None:
            response = self.session.get(url=url)
        else:
            response = self.session.get(url=url, data=data)

        return self._type_based_return(response)

    def get_pict(self, url):
        self.session.headers.update({
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Dest": "image"
        })
        img = self.get(url=url)
        self.session.headers.update({
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty"
        })
        return PreserveResponse(img)

    def _type_based_return(self, response):
        if self.type == PRESERVE_SESSION:
            return PreserveResponse(response)
        elif self.type == RESERVE_SESSION:
            return ReserveResponse(response)
        else:
            return Response(response)

