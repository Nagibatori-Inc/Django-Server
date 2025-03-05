from rest_framework.authentication import BasicAuthentication

from authentication.utils import make_phone_uniform


class CustomBasicAuthentication(BasicAuthentication):
    def authenticate_credentials(self, userid, password, request=None):
        userid = make_phone_uniform(userid)
        return super().authenticate_credentials(userid, password, request)
