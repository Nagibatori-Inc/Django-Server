from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED
from rest_framework.views import APIView

from support.selectors.answers import get_answers_for_message
from support.selectors.messages import get_user_messages, get_message_by_id
from support.serializers import SupportAnswerSerializer, SupportMessageSerializerIn, SupportMessageSerializerOut

SWAGGER_SUPPORT_CLIENT_TAG = "Поддержка (клиент)"
SWAGGER_SUPPORT_AGENT_TAG = "Поддержка (агент)"


# Create your views here.
class ClientSupportMessagesAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        description='Отправить сообщение в поддержку',
        tags=[SWAGGER_SUPPORT_CLIENT_TAG],
        request=SupportMessageSerializerIn,
        responses={
            status.HTTP_200_OK: SupportMessageSerializerIn,
        },
    )
    def post(self, request: Request):
        message_data = SupportMessageSerializerIn(data=request.data)
        message_data.is_valid(raise_exception=True)

        message_data.save(user=request.user)
        return Response(status=HTTP_201_CREATED)

    @extend_schema(
        description='Посмотреть сообщения в поддержку',
        tags=[SWAGGER_SUPPORT_CLIENT_TAG],
        request={},
        responses={
            status.HTTP_200_OK: SupportMessageSerializerOut(many=True),
        },
    )
    def get(self, request: Request):
        user_messages = get_user_messages(user=request.user)  # type: ignore[arg-type]
        serializer_messages = SupportMessageSerializerOut(user_messages, many=True)

        return Response(status=HTTP_200_OK, data=serializer_messages.data)


class AgentSupportMessagesAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    @extend_schema(
        description='Ответить на сообщение',
        tags=[SWAGGER_SUPPORT_AGENT_TAG],
        request=SupportAnswerSerializer,
        responses={
            status.HTTP_200_OK: SupportAnswerSerializer,
        },
    )
    def post(self, request: Request, message_id: int):
        answer_data = SupportAnswerSerializer(data=request.data)
        answer_data.is_valid(raise_exception=True)

        message = get_message_by_id(message_id=message_id)
        answer = answer_data.save(agent=request.user, message=message)
        return Response(status=HTTP_201_CREATED, data=SupportAnswerSerializer(instance=answer).data)

    @extend_schema(
        description='Получить ответы на сообщения',
        tags=[SWAGGER_SUPPORT_AGENT_TAG],
        request={},
        responses={
            status.HTTP_200_OK: SupportAnswerSerializer,
        },
    )
    def get(self, request: Request, message_id: int):
        answers = get_answers_for_message(message_id)

        return Response(status=HTTP_200_OK, data=SupportAnswerSerializer(instance=answers, many=True).data)
