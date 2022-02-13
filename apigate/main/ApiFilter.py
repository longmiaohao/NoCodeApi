import abc


class ApiFilter(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def request(self, request):
        """
        core.py 调用接口前执行
        """
        pass

    @abc.abstractmethod
    def response(self, request, response):
        """
        返回结果之前执行
        """
        pass

