from rest_framework.exceptions import ValidationError

from booking.models import Advert


def get_advert_by_id(pk: int) -> Advert:
    try:
        advert = Advert.objects.get(pk=pk)
    except Advert.DoesNotExist:
        raise ValidationError("Нет такого объявления")

    return advert
