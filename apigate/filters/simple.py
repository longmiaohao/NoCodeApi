from apigate.main.ApiFilter import ApiFilter
from django.http import JsonResponse


class userlist(ApiFilter):
    def __init__(self, request):
        pass

    def request(self, request):
        request.data['password'] = 1111
        # if request.data['username'] != 'admin':
        #     return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "调用自定义request拦截"}, json_dumps_params={"ensure_ascii": False})

    def response(self, request, response):
        if request.data['username'] != 'admin':
            print("调用自定义response")
            res = JsonResponse({"RTN_CODE": "00", "RTN_MSG": "调用自定义response拦截"}, json_dumps_params={"ensure_ascii": False})
            return res
        else:
            return response
