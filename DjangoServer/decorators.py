from functools import wraps
from typing import Callable

from django.core.exceptions import ObjectDoesNotExist, EmptyResultSet, FieldDoesNotExist, FieldError, PermissionDenied
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, AuthenticationFailed, ParseError
from rest_framework.response import Response

from DjangoServer.service import RestService


class ServiceExceptionHandler:
    def __init__(self, service: RestService):
        self.__service = service

    @property
    def service(self) -> RestService:
        return self.__service

    @service.setter
    def service(self, service) -> None:
        self.__service = service

    def wrap(self, method) -> Callable:
        """
        Декоратор, который оборачивает метод сервиса в обработку исключений

        :param method:
        :return:
        """

        @wraps(method)
        def wrapper(*args, **kwargs):
            try:
                return method(*args, **kwargs)
            except Exception as e:
                return self.handle_exception(e)

        return wrapper

    def handle_exception(self, exception) -> RestService:
        """
        Определяет, как обрабатывать исключение

        :param exception:
        :return:
        """
        if isinstance(exception, (ObjectDoesNotExist, EmptyResultSet)):
            return self.handle_404(exception)

        if isinstance(exception, PermissionDenied):
            return self.handle_403(exception)

        if isinstance(exception, (NotAuthenticated, AuthenticationFailed)):
            return self.handle_401(exception)

        if isinstance(exception, (FieldDoesNotExist, FieldError, ParseError, ValueError, TypeError)):
            return self.handle_400(exception)

        raise exception

    def handle_404(self, exception):
        """
        Обработка ошибки 404

        :param exception:
        :return:
        """
        self.service.response = Response({'err_msg': str(exception)}, status=status.HTTP_404_NOT_FOUND)
        return self.service

    def handle_403(self, exception):
        """
        Обработка ошибки 403

        :param exception:
        :return:
        """
        self.service.response = Response({'err_msg': str(exception)}, status=status.HTTP_403_FORBIDDEN)
        return self.service

    def handle_401(self, exception):
        """
        Обработка ошибки 401

        :param exception:
        :return:
        """
        self.service.response = Response({'err_msg': str(exception)}, status=status.HTTP_401_UNAUTHORIZED)
        return self.service

    def handle_400(self, exception):
        """
        Обработка ошибки 400

        :param exception:
        :return:
        """
        self.service.response = Response({'err_msg': str(exception)}, status=status.HTTP_400_BAD_REQUEST)
        return self.service


def handle_service_method(method: Callable):
    """
    Декоратор для обработки исключений в методах сервисов
    """

    @wraps(method)
    def wrapper(*args, **kwargs):
        self = args[0] if args else RestService()
        handler = ServiceExceptionHandler(self)
        wrapped_method = handler.wrap(method)
        return wrapped_method(self, *args, **kwargs)

    return wrapper
