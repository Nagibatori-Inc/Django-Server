from functools import wraps
from typing import Callable

import structlog
from django.core.exceptions import ObjectDoesNotExist, EmptyResultSet, FieldDoesNotExist, FieldError, PermissionDenied
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, AuthenticationFailed, ParseError
from rest_framework.response import Response

from DjangoServer.service import RestService

logger = structlog.get_logger(__name__)


class ServiceExceptionHandler:
    """
    Класс декоратора для обработки исключений в методах сервисов
    """
    class ServiceExceptionWrapper:
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
                    args = args[1::] if isinstance(args[0], ServiceExceptionHandler) else args
                    return method(*args, **kwargs)
                except Exception as e:
                    logger.error(
                        'catch and handle error in service method', service=self.service, method=method, exception=e
                    )
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

    def __init__(self, method: Callable):
        self.__method = method

    def __call__(self, *args, **kwargs):
        """
        Декоратор для обработки исключений в методах сервисов
        """
        service = args[0] if args else RestService()
        handler = self.ServiceExceptionWrapper(service)
        wrapped_method = handler.wrap(self.__method)
        return wrapped_method(self, *args, **kwargs)
