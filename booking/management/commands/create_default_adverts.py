from datetime import datetime

from django.core.management import call_command
from django.core.management.base import BaseCommand

from authentication.models import Profile
from booking.models import AdvertStatus
from booking.serializers import AdvertSerializer
from booking.services import AdvertService


class Command(BaseCommand):
    help = 'Создаёт дефолтные объявления для дефолтного пользователя'

    def handle(self, *args, **kwargs):
        profile = Profile.objects.filter(user__email='defaultuser@example.com').first()

        if not profile:
            self.stdout.write('Пользователь не найден. Создаю...')
            call_command('create_default_profile')
            profile = Profile.objects.get(user__email='defaultuser@example.com')

        defaults = [
            {
                'title': 'Объявление 1',
                'description': 'Описание 1',
                'price': 1000,
                'views': 12,
                'status': AdvertStatus.ACTIVE,
                'activated_at': datetime.now(),
                'phone': '89178432456',
            },
            {
                'title': 'Объявление 2',
                'description': 'Описание 2',
                'price': 1500,
                'views': 45,
                'status': AdvertStatus.ACTIVE,
                'activated_at': datetime.now(),
                'phone': '89178432456',
            },
            {
                'title': 'Объявление 3',
                'description': 'Описание 3',
                'price': 20000,
                'views': 456,
                'status': AdvertStatus.ACTIVE,
                'activated_at': datetime.now(),
                'phone': '89178432456',
            },
            {
                'title': 'Объявление 4',
                'description': 'Описание 4',
                'price': 15300,
                'views': 87,
                'status': AdvertStatus.ACTIVE,
                'activated_at': datetime.now(),
                'phone': '89178432456',
            },
            {
                'title': 'Объявление 5',
                'description': 'Описание 5',
                'price': 345670,
                'views': 785,
                'status': AdvertStatus.ACTIVE,
                'activated_at': datetime.now(),
                'phone': '89178432456',
            },
            {
                'title': 'Объявление 6',
                'description': 'Описание 6',
                'price': 150000,
                'views': 231,
                'status': AdvertStatus.ACTIVE,
                'activated_at': datetime.now(),
                'phone': '89178432456',
            },
            {
                'title': 'Объявление 7',
                'description': 'Описание 7',
                'price': 130500,
                'views': 6573,
                'status': AdvertStatus.ACTIVE,
                'activated_at': datetime.now(),
                'phone': '89178432456',
            },
        ]

        for data in defaults:
            serializer = AdvertSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            AdvertService.advertise(serializer, profile)

        self.stdout.write(self.style.SUCCESS('Объявления успешно созданы.'))
