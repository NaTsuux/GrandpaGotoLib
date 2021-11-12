import requests
from .utils import get_cookie_jar
from .utils import get_header_dict
import querycontent
from .response import PreserveResponse, ReserveResponse


class Session:

    def __init__(self):
        self.session = requests.session()
        self.session.cookies = get_cookie_jar()
        self.session.headers = get_header_dict()
        self.url = "https://wechat.v2.traceint.com/index.php/graphql/"

    def _type_based_return(self, url, response):
        if type(url) is querycontent.Preserve:
            return PreserveResponse(response)
        elif type(url) is querycontent.Reserve:
            return ReserveResponse(response)
        else:
            return response

    def post(self, data="", url=None):
        if url is None:
            url = self.url
        response = self.session.post(url=url, data=data)
        
        return self._type_based_return(url, response)

    def get(self, url=None, data=None):
        if url is None:
            url = self.url

        if data is None:
            response = self.session.get(url=url)
        else:
            response = self.session.get(url=url, data=data)

        return self._type_based_return(url, response)

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


def session():
    return Session()
