from django.db import transaction
from rest_framework import status
from rest_framework.response import Response


class RestService:
    """
    Базовый класс для реализации сервисной логики проекта

    # TODO: Для работы сервисов через цепочку методов, обрабатывающих действия над объектами, и формирующих HTTP ответы,
    требуется наследоваться от него

    Fields:
        + response (Response): Необязательное поле,
        нужное для отправки ответа при публикации объявления или его изменения
        + should_commit (Bool): Статус коммита транзакции в базу данных

    Methods:
        + _finalize_transaction(): Приватный метод для коммита транзакции в базу данных
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

    def __init__(self, response: Response = None, should_commit: bool = True):
        self.__response = response
        self.__should_commit = should_commit

    @property
    def response(self):
        return self.__response

    @response.setter
    def response(self, response: Response):
        self.__response = response

    @property
    def should_commit(self):
        return self.__should_commit

    @should_commit.setter
    def should_commit(self, should_commit: bool):
        self.__should_commit = should_commit

    def _finalize_transaction(self):
        """
        Финализируем транзакцию: коммитим, если всё хорошо, иначе откатываем.
        """
        if self.response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]:
            self.should_commit = True
        else:
            self.should_commit = False
            self.response = Response(status=status.HTTP_400_BAD_REQUEST)

        if self.should_commit:
            transaction.set_autocommit(True)
        else:
            transaction.rollback()

        return self.response

    def ok(self):
        """
        Если действия с объявлениями прошли успешно, возвращает `200 OK`, иначе продолжает цепочку

        :return: Response | RestService
        """
        if self.response is None:
            self.response = Response(status=status.HTTP_200_OK)

        return self

    def or_else_send(self, status_code):
        """
        Продолжает цепочку создания ответа от АПИ. Возвращает полученный `status_code`,
        если в цепочке не создались требуемые ответы

        :param status_code: (str | int) возвращаемый статус код ответа
        :return: Response | RestService
        """
        return self.response or Response(status=status_code)

    def or_else_400(self):
        return self.or_else_send(status.HTTP_400_BAD_REQUEST)

    def or_else_401(self):
        return self.or_else_send(status.HTTP_401_UNAUTHORIZED)

    def or_else_403(self):
        return self.or_else_send(status.HTTP_403_FORBIDDEN)

    def or_else_404(self):
        return self.or_else_send(status.HTTP_404_NOT_FOUND)

    def or_else_422(self):
        return self.or_else_send(status.HTTP_422_UNPROCESSABLE_ENTITY)

    def respond_or_else_send(self, response: callable, status_code):
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