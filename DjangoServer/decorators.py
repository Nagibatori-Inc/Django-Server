from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response

from DjangoServer.service import RestService


class ServiceExceptionHandler:
    def __init__(self, service: RestService):
        self.__service = service

    @property
    def service(self):
        return self.__service

    @service.setter
    def service(self, value):
        self.__service = value

    def wrap(self, method, *args, **kwargs):
        return


def handle_404(service, method, *args, **kwargs):
    try:
        return method(*args, **kwargs)

    except ObjectDoesNotExist as e:
        service.response = Response(
            {'err_msg': str(e)},
            status=status.HTTP_404_NOT_FOUND
        )

    return service


def handle_service_exceptions(method):
    def wrapper(self, *args, **kwargs):
        try:
            return method(*args, **kwargs)

        except ObjectDoesNotExist as e:
            self.response = Response(
                {'err_msg': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

        return self

    return wrapper

