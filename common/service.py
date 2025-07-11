from typing import Type, Optional, Callable

import structlog
from django.db import transaction
from rest_framework import status
from rest_framework import serializers
from rest_framework.response import Response

logger = structlog.get_logger(__name__)


class RestService:
    """
    Базовый класс для реализации сервисной логики проекта

    TODO: Для работы сервисов через цепочку методов, обрабатывающих действия над объектами, и формирующих HTTP ответы, требуется наследоваться от него

    Fields:
        + response (Response): Необязательное поле,
        нужное для отправки ответа при публикации объявления или его изменения
        + should_commit (Bool): Статус коммита транзакции в базу данных

    Methods:
        + _finalize_transaction(): Приватный метод для коммита транзакции в базу данных
        + serialize(serializer):
        + ok(): Если действия с объявлениями прошли успешно, возвращает `200 OK`, иначе продолжает цепочку
        + or_else_send(status_code): Продолжает цепочку создания ответа от АПИ. Возвращает полученный `status_code`,
        если в цепочке не создались требуемые ответы
        + or_else_4xx(): Методы, вызывающие or_else_send(4xx) с тем кодом, что указан в названии метода
        + respond_or_else_send(response, status_code): Вызывает указанный метод отправки ответа (Response'а),
        используемый в цепочке формирования Response'а, если все действия прошли успешно, иначе ответ со статусом,
        указанным в `status_code`

    Properties:
        + response(): Возвращает объект ответа
        + response(response): Сеттер для поля `response`
        + should_commit(): Возвращает статус коммита
        + should_commit(should_commit): Сеттер для поля `should_commit`
    """

    def __init__(self, response: Optional[Response] = None, should_commit: bool = True):
        self.__response = response
        self.__should_commit = should_commit

    @property
    def response(self) -> Optional[Response]:
        return self.__response

    @response.setter
    def response(self, response: Response) -> None:
        self.__response = response

    @property
    def should_commit(self) -> bool:
        return self.__should_commit

    @should_commit.setter
    def should_commit(self, should_commit: bool) -> None:
        self.__should_commit = should_commit

    def _finalize_transaction(self) -> Optional[Response]:
        """
        Финализируем транзакцию: коммитим, если всё хорошо, иначе откатываем.
        """
        if self.response and self.response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]:
            self.should_commit = True
        else:
            self.should_commit = False
            self.response = Response(status=status.HTTP_400_BAD_REQUEST)

        if self.should_commit:
            transaction.set_autocommit(True)
        else:
            transaction.rollback()

        return self.response

    def serialize(self, serializer: Type[serializers.ModelSerializer]):
        pass

    def ok(self, body=None):
        """
        Если действия с объектами сервиса прошли успешно, возвращает `200 OK`, иначе продолжает цепочку

        :return: RestService
        """
        if self.response is None:
            if body is not None:
                self.response = Response(body, status=status.HTTP_200_OK)

            else:
                self.response = Response(status=status.HTTP_200_OK)

        elif body is not None:
            self.response.data = body

        return self

    def or_else_send(self, status_code) -> Optional[Response]:
        """
        Продолжает цепочку создания ответа от АПИ. Возвращает полученный `status_code`,
        если в цепочке не создались требуемые ответы

        :param status_code: (str | int) возвращаемый статус код ответа
        :return: Response | RestService
        """
        return self.response or Response(status=status_code)

    def or_else_400(self) -> Optional[Response]:
        return self.or_else_send(status.HTTP_400_BAD_REQUEST)

    def or_else_401(self) -> Optional[Response]:
        return self.or_else_send(status.HTTP_401_UNAUTHORIZED)

    def or_else_403(self) -> Optional[Response]:
        return self.or_else_send(status.HTTP_403_FORBIDDEN)

    def or_else_404(self) -> Optional[Response]:
        return self.or_else_send(status.HTTP_404_NOT_FOUND)

    def or_else_422(self) -> Optional[Response]:
        return self.or_else_send(status.HTTP_422_UNPROCESSABLE_ENTITY)

    def respond_or_else_send(self, response: Callable, status_code) -> Optional[Response]:
        """
        Вызывает указанный метод отправки ответа (Response'а), используемый в цепочке формирования Response'а,
        если все действия прошли успешно, иначе ответ со статусом, указанным в `status_code`

        :param response: (callable) метод, используемый в цепочке формирования Response'а
        :param status_code: (str | int) возвращаемый статус код ответа
        :return: Response | RestService
        """
        return response() or Response(status=status_code)

    def __getattr__(self, name):
        """
        Если кто-то пытается вызвать метод/поле, которого нет,
        но у нас есть self.response, значит, разработчик забыл вызвать or_else_send().
        Автоматически возвращаем `response` и завершаем транзакцию.
        """
        if self.response:
            return self._finalize_transaction()

        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
