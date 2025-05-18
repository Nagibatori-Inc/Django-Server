from django.core.management.base import BaseCommand

from authentication.services.profile import ProfileManagerService
from authentication.models import Profile


class Command(BaseCommand):
    help = 'Создаёт дефолтный профиль, если его нет'

    def handle(self, *args, **kwargs):
        if not Profile.objects.filter(user__email='defaultuser@example.com').exists():
            ProfileManagerService.create(
                phone='79112345678',
                password='defaultpassword',
                first_name='default',
                email='defaultuser@example.com',
                profile_name='defaultprofile',
                profile_type='IND',
            )
            self.stdout.write(self.style.SUCCESS('Дефолтный профиль создан.'))
        else:
            self.stdout.write(self.style.NOTICE('Дефолтный профиль уже существует.'))
