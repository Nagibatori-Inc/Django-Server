from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.views import APIView

from support.models import SupportAnswer
from support.serializers import SupportMessageSerializer

SWAGGER_SUPPORT_CLIENT_TAG = "Поддержка (клиент)"
SWAGGER_SUPPORT_AGENT_TAG = "Поддержка (агент)"


# Create your views here.
class ClientSupportMessagesAPIView(APIView):
    serializer_class = SupportMessageSerializer

    @extend_schema(
        description='Отправить сообщение в поддержку',
        tags=[SWAGGER_SUPPORT_CLIENT_TAG],
        request={},
        responses={
            status.HTTP_200_OK: serializer_class,
        },
    )
    def post(self):
        pass

    @extend_schema(
        description='Посмотреть свои сообщения в поддержку',
        tags=[SWAGGER_SUPPORT_CLIENT_TAG],
        request={},
        responses={
            status.HTTP_200_OK: serializer_class(many=True),
        },
    )
    def get(self):
        pass


class AgentSupportMessagesAPIView(APIView):
    serializer_class = SupportAnswer

    @extend_schema(
        description='Ответить на сообщение',
        tags=[SWAGGER_SUPPORT_AGENT_TAG],
        request={},
        responses={
            status.HTTP_200_OK: serializer_class,
        },
    )
    def post(self):
        pass

    @extend_schema(
        description='Получить ответы на сообщения',
        tags=[SWAGGER_SUPPORT_AGENT_TAG],
        request={},
        responses={
            status.HTTP_200_OK: serializer_class,
        },
    )
    def get(self):
        pass
