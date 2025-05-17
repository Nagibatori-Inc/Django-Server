from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, OpenApiResponse
from knox.auth import TokenAuthentication
from knox.views import LogoutView, LogoutAllView
from rest_framework import exceptions, HTTP_HEADER_ENCODING, status
from rest_framework.authentication import BasicAuthentication
from rest_framework.request import Request

from authentication.utils import make_phone_uniform
from authentication.views import AUTHENTIFICATION_SWAGGER_TAG
from common.swagger.schema import AUTH_ERRORS_SCHEMA_RESPONSES


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


@extend_schema(
    tags=[AUTHENTIFICATION_SWAGGER_TAG],
    request={},
    responses={
        status.HTTP_204_NO_CONTENT: OpenApiResponse(description='Успешный выход'),
        **AUTH_ERRORS_SCHEMA_RESPONSES,
        status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description='Internal Server Error'),
    },
)
class CookieTokenLogout(LogoutView):
    authentication_classes = [CookieTokenAuthentication]


@extend_schema(
    tags=[AUTHENTIFICATION_SWAGGER_TAG],
    request={},
    responses={
        status.HTTP_204_NO_CONTENT: OpenApiResponse(description='Успешный выход из всех сессий'),
        **AUTH_ERRORS_SCHEMA_RESPONSES,
        status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description='Internal Server Error'),
    },
)
class CookieTokenLogoutAll(LogoutAllView):
    authentication_classes = [CookieTokenAuthentication]
