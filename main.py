import requests
import os

url = "https://cdn14.hentai2.net/uploads/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63030068)",
}

dir = '376687/'
suffix = '.jpg'
os.mkdir(dir)

for i in range(1, 250):
    uurl = url + dir + str(i) + suffix
    print(uurl)
    req = requests.get(uurl)
    if req.status_code == 200:
        with open(dir + str(i) + suffix, 'wb') as f:
            f.write(req.content)
        f.close()
        print(i)
    else:
        break
