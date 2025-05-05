from django.utils.translation import gettext_lazy as _
from knox.auth import TokenAuthentication
from knox.views import LogoutView, LogoutAllView
from rest_framework import exceptions, HTTP_HEADER_ENCODING
from rest_framework.authentication import BasicAuthentication
from rest_framework.request import Request

from authentication.utils import make_phone_uniform


class CustomBasicAuthentication(BasicAuthentication):
    def authenticate_credentials(self, userid, password, request=None):
        userid = make_phone_uniform(userid)
        return super().authenticate_credentials(userid, password, request)


class CookieTokenAuthentication(TokenAuthentication):
    @staticmethod
    def get_cookie_authorization(request: Request):
        auth = request.COOKIES.get("Authorization", b'')
        if isinstance(auth, str):
            auth = auth.encode(HTTP_HEADER_ENCODING)
        return auth

    def authenticate(self, request: Request):
        auth = CookieTokenAuthentication.get_cookie_authorization(request).split()
        prefix = self.authenticate_header(request).encode()

        if not auth:
            return None
        if auth[0].lower() != prefix.lower():
            # Authorization header is possibly for another backend
            return None
        if len(auth) == 1:
            msg = _('Invalid token header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)  # type: ignore[arg-type]
        elif len(auth) > 2:
            msg = _('Invalid token header. ' 'Token string should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)  # type: ignore[arg-type]

        user, auth_token = self.authenticate_credentials(auth[1])
        return (user, auth_token)


class CookieTokenLogout(LogoutView):
    authentication_classes = [CookieTokenAuthentication]


class CookieTokenLogoutAll(LogoutAllView):
    authentication_classes = [CookieTokenAuthentication]
