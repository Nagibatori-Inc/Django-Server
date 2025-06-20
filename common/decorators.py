from functools import wraps

from django.core.exceptions import ObjectDoesNotExist, EmptyResultSet, FieldDoesNotExist, FieldError, PermissionDenied
from rest_framework import status
from rest_framework.response import Response

from common.service import RestService


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

    except ObjectDoesNotExist or EmptyResultSet as e:  #  type: ignore[truthy-function]
        service.response = Response({'err_msg': str(e)}, status=status.HTTP_404_NOT_FOUND)

    return service


def handle_service_exceptions(method):
    """
    Декоратор для обработки исключений внутри сервисных методов.
    """

    @wraps(method)
    def wrapper(*args, **kwargs):
        print(f'method: {method}, args: {args}, kwargs: {kwargs}')
        try:
            return method(*args, **kwargs)

        except (ObjectDoesNotExist, EmptyResultSet) as e:
            response = Response({'err_msg': str(e)}, status=status.HTTP_404_NOT_FOUND)  # noqa F841

        except (FieldDoesNotExist, FieldError, ValueError, TypeError) as e:
            response = Response({'err_msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)  # noqa F841

        except PermissionDenied as e:
            response = Response({'err_msg': str(e)}, status=status.HTTP_403_FORBIDDEN)  # noqa F841

        return {}

    return wrapper
