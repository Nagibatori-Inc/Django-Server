from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response


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


def handle_400(method):
    pass
