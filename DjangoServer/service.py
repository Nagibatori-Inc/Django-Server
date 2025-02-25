from rest_framework import status
from rest_framework.response import Response


class RestService:
    """
    Базовый класс для реализации сервисной логики проекта

    [!TIP]
    Для работы сервисов через цепочку методов, обрабатывающих действия над объектами, и формирующих HTTP ответы,
    требуется наследоваться от него

    Fields:
        + response (Response): Необязательное поле,
        нужное для отправки ответа при публикации объявления или его изменения
        + response_finalized (Bool): Флаг, который фиксирует момент, когда уже создан `response`

    Methods:
        + ok(): Если действия с объявлениями прошли успешно, возвращает `200 OK`, иначе продолжает цепочку
        + or_else_send(status_code): Продолжает цепочку создания ответа от АПИ. Возвращает полученный `status_code`,
        если в цепочке не создались требуемые ответы
        + respond_or_else_send(response, status_code): Вызывает указанный метод отправки ответа (Response'а),
        используемый в цепочке формирования Response'а, если все действия прошли успешно, иначе ответ со статусом,
        указанным в `status_code`

    Properties:
        + response(): Возвращает объект ответа
        + response(response): Сеттер для поля `response`
        + response_finalized(): Возвращает приватное поле __response_finalized
    """

    def __init__(self, response: Response = None, response_finalized: bool = False):
        self.__response = response
        self.__response_finalized = response_finalized

    @property
    def response(self):
        return self.__response

    @response.setter
    def response(self, response: Response):
        self.__response = response

    @property
    def response_finalized(self):
        return self.__response_finalized

    def _finalize_response(self):
        """
        Если уже есть Response, дальнейшие вызовы методов не изменяют его

        :return: Response | RestService
        """
        if isinstance(self.response, Response):
            return self.response

        return self

    def ok(self):
        """
        Если действия с объявлениями прошли успешно, возвращает `200 OK`, иначе продолжает цепочку

        :return: Response | RestService
        """
        if (self.response is None) or (not self.response.status_code != status.HTTP_200_OK):
            self.response = Response(status=status.HTTP_200_OK)

        return self._finalize_response()

    def or_else_send(self, status_code):
        """
        Продолжает цепочку создания ответа от АПИ. Возвращает полученный `status_code`,
        если в цепочке не создались требуемые ответы

        :param status_code: (str | int) возвращаемый статус код ответа
        :return: Response | RestService
        """
        return self.response or Response(status=status_code)

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
        Автоматически возвращает Response, если кто-то забыл вызвать or_else_send().
        """
        if self.response_finalized:
            raise AttributeError(f"Response уже был создан, вызов `{name}` невозможен.")

        return self.__dict__.get(name)

    def __repr__(self):
        """
        Автоматически возвращает Response, если его забыли обработать.
        """
        return repr(self.response) \
            if isinstance(self.response, Response) \
            else super().__repr__()