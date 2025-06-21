from datetime import datetime
import base64

import requests
from django.core.management import call_command
from django.core.management.base import BaseCommand

from authentication.models import Profile
from booking.models import AdvertStatus
from booking.serializers import AdvertCreationSerializer
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
                'logo_url': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRsWGsOwujVO2TxxPn2TmaW0Fb2ofXeCpKu4A&s',
            },
            {
                'title': 'Объявление 2',
                'description': 'Описание 2',
                'price': 1500,
                'views': 45,
                'status': AdvertStatus.ACTIVE,
                'activated_at': datetime.now(),
                'phone': '89178432456',
                'logo_url': 'https://totalarch.com/files/business/free/wheel_loader_01.jpg',
            },
            {
                'title': 'Объявление 3',
                'description': 'Описание 3',
                'price': 20000,
                'views': 456,
                'status': AdvertStatus.ACTIVE,
                'activated_at': datetime.now(),
                'phone': '89178432456',
                'logo_url': 'https://hyundai.ru.com/api/v1/files/categories/cover_d35fd_a6435170a9c5a7d95f2178c8b160ade3.jpg',
            },
            {
                'title': 'Объявление 4',
                'description': 'Описание 4',
                'price': 15300,
                'views': 87,
                'status': AdvertStatus.ACTIVE,
                'activated_at': datetime.now(),
                'phone': '89178432456',
                'logo_url': 'https://big-center.ru/upload/resize_cache/iblock/e2b/gy6g0jtwi38iy43xwi1lk34haq8z50j3/416_312_2/1_result.webp',
            },
            {
                'title': 'Объявление 5',
                'description': 'Описание 5',
                'price': 345670,
                'views': 785,
                'status': AdvertStatus.ACTIVE,
                'activated_at': datetime.now(),
                'phone': '89178432456',
                'logo_url': 'https://abiznews.net/wp-content/uploads/2023/09/%D1%81%D0%BF%D0%B5%D1%86%D1%82%D0%B5%D1%85%D0%BD%D0%B8%D0%BA%D0%B0.jpg',
            },
            {
                'title': 'Объявление 6',
                'description': 'Описание 6',
                'price': 150000,
                'views': 231,
                'status': AdvertStatus.ACTIVE,
                'activated_at': datetime.now(),
                'phone': '89178432456',
                'logo_url': 'https://mosdoroga.ru/wp-content/uploads/2017/08/stroitelnaya-spectekhnika.jpg',
            },
            {
                'title': 'Объявление 7',
                'description': 'Описание 7',
                'price': 130500,
                'views': 6573,
                'status': AdvertStatus.ACTIVE,
                'activated_at': datetime.now(),
                'phone': '89178432456',
                'logo_url': 'https://ostrovmashin.ru/upload/resize_cache/iblock/8ad/860_600_1/8ad6d93e6a277d2a2edd18b5f53460ba.jpg',
            },
        ]

        for index, data in enumerate(defaults):
            logo_url = data.pop('logo_url', '')

            if not logo_url or len(logo_url) == 0:
                self.stdout.write(self.style.WARNING(f'Нет logo_url для объявления {index + 1}'))
                continue

            try:
                response = requests.get(logo_url)
                response.raise_for_status()

                mime_type = response.headers.get('Content-Type', 'image/jpeg')
                if not mime_type.startswith('image/'):
                    raise ValueError(f'Некорректный MIME-тип: {mime_type}')

                encoded_string = base64.b64encode(response.content).decode('utf-8')
                data['logo'] = f'data:{mime_type};base64,{encoded_string}'

                serializer = AdvertCreationSerializer(data=data)
                serializer.is_valid(raise_exception=True)
                AdvertService.advertise(serializer, profile)

                self.stdout.write(self.style.SUCCESS(f'Объявление "{index + 1}" создано.'))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Ошибка при создании объявления {index + 1}: {e}'))

        self.stdout.write(self.style.SUCCESS('Все объявления обработаны.'))
