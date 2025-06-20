from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_409_CONFLICT
from rest_framework.views import APIView

from authentication.misc.custom_auth import CookieTokenAuthentication
from booking.permissions import IsAdvertOwnerOrReadOnly
from booking.services import PromotionService
from common.swagger.schema import SWAGGER_NO_RESPONSE_BODY, DEFAULT_PUBLIC_API_SCHEMA_RESPONSES
from payments.models import PaymentStatus
from payments.selectors import get_payment_by_external_id
from payments.serializers import PaymentSerializer, WebHookEventSerializer
from payments.services.purchase_processors import YooKassa


PAYMENTS_SWAGGER_TAG = "Оплата"


class PromotionPurchaseView(APIView):
    authentication_classes = [CookieTokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdvertOwnerOrReadOnly]

    @extend_schema(
        tags=[PAYMENTS_SWAGGER_TAG],
        description='Покупка продвижения',
        request=PaymentSerializer,
        responses={
            status.HTTP_200_OK: inline_serializer(
                name='PaymentResponse',
                fields={'confirmation_url': serializers.CharField()},
            ),
            **DEFAULT_PUBLIC_API_SCHEMA_RESPONSES,
        },
    )
    def post(self, request: Request):
        payment_data = PaymentSerializer(data=request.data)
        payment_data.is_valid(raise_exception=True)

        advert = payment_data.validated_data["advert"]

        self.check_object_permissions(request, advert)

        if advert.is_promoted:
            return Response(status=HTTP_409_CONFLICT)

        payment = payment_data.save(user=request.user)
        confirm_url = YooKassa(payment).init_transaction()

        return Response(status=HTTP_200_OK, data={"confirmation_url": confirm_url})


class PaymentSystemWebHookView(APIView):
    @extend_schema(
        tags=[PAYMENTS_SWAGGER_TAG],
        description='Вебхук для уведомлений от банка',
        request=WebHookEventSerializer,
        responses={
            status.HTTP_200_OK: SWAGGER_NO_RESPONSE_BODY,
            status.HTTP_500_INTERNAL_SERVER_ERROR: SWAGGER_NO_RESPONSE_BODY,
            **DEFAULT_PUBLIC_API_SCHEMA_RESPONSES,
        },
    )
    def post(self, request: Request):
        webhook_data = WebHookEventSerializer(data=request.data)
        webhook_data.is_valid(raise_exception=True)

        event = webhook_data.validated_data.get("event")
        external_payment = webhook_data.validated_data.get("object")
        internal_payment = get_payment_by_external_id(external_payment["id"])

        YooKassa(internal_payment).finalize_transaction(event, external_payment)
        if internal_payment.status == PaymentStatus.SUCCESSFUL:
            PromotionService().promote("Базовое", 1, internal_payment.advert)

        return Response(status=HTTP_200_OK)
