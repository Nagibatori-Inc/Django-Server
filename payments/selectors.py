from rest_framework.exceptions import APIException

from payments.models import Payment


def get_payment_by_external_id(id: str) -> Payment:
    try:
        payment = Payment.objects.get(external_transaction_id=id)
    except Payment.DoesNotExist:
        raise APIException()

    return payment
