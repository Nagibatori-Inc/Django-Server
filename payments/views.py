from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_409_CONFLICT
from rest_framework.views import APIView

from authentication.misc.custom_auth import CookieTokenAuthentication
from booking.permissions import IsAdvertOwnerOrReadOnly
from booking.services import PromotionService
from payments.models import PaymentStatus
from payments.selectors import get_payment_by_external_id
from payments.serializers import PaymentSerializer, WebHookEventSerializer
from payments.services.purchase_processors import YooKassa


class PromotionPurchaseView(APIView):
    authentication_classes = [CookieTokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdvertOwnerOrReadOnly]

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
