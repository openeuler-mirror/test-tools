import requests
from Aops_Api_Auto_Test.utils.LogUtil import my_log


class Request:
    def __init__(self):
        self.log = my_log("Requests")

    def requests_api(self, url, params=None, json=None, files=None, headers=None, cookies=None, method="get"):
        if method == "get":
            self.log.debug("发送get请求")
            res = requests.get(url, json=json, params=params, headers=headers, cookies=cookies)
            self.log.debug("发送的data数据==>> %s", str(params))
        elif method == "post":
            self.log.debug("发送post请求")
            res = requests.post(url, json=json, data=params, files=files, headers=headers, cookies=cookies)
        elif method == "delete":
            self.log.debug("发送delete请求")
            res = requests.delete(url, json=json, data=params, headers=headers, cookies=cookies)
        code = res.status_code
        try:
            body = res.json()
        except Exception as e:
            body = res.text
        res_data = dict()
        res_data["code"] = code
        res_data["body"] = body
        return res_data

    def get(self, url, **kwargs):
        return self.requests_api(url, method="get", **kwargs)

    def post(self, url, **kwargs):
        return self.requests_api(url, method="post", **kwargs)

    def delete(self, url, **kwargs):
        return self.requests_api(url, method="delete", **kwargs)

