from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiResponse, OpenApiExample
from knox.views import LoginView as KnoxLoginView, LogoutView, LogoutAllView
from rest_framework import status, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from authentication.misc.custom_auth import CustomBasicAuthentication, CookieTokenAuthentication
from authentication.permissions import IsProfileOwnerOrReadOnly
from authentication.selectors.profile import get_profile_with_user, get_user_with_profile_by_phone
from authentication.serializers import (
    ProfileSerializer,
    SignUpRequestSerializer,
    VerificationRequestSerializer,
    PhoneSerializer,
    PasswordResetSerializer,
    ProfileOwnerSerializer,
)
from authentication.services.profile import ProfileManagerService, PasswordManagerService
from authentication.services.verification import BaseVerificationService
from authentication.tasks import send_sms_task
from authentication.utils import make_phone_uniform
from DjangoServer.settings import MESSAGE_TEMPLATE
from common.swagger.schema import (
    SWAGGER_NO_RESPONSE_BODY,
    DEFAULT_PRIVATE_API_ERRORS_SCHEMA_RESPONSES,
    DEFAULT_PUBLIC_API_SCHEMA_RESPONSES,
    AUTH_ERRORS_SCHEMA_RESPONSES,
)

AUTHENTIFICATION_SWAGGER_TAG = 'Авторизация'
PROFILE_SWAGGER_TAG = 'Профили'


@extend_schema(
    tags=[AUTHENTIFICATION_SWAGGER_TAG],
    description='Войти',
    request={},
    responses={
        status.HTTP_200_OK: inline_serializer(
            name='LoginResponse',
            fields={'expiry': serializers.DateTimeField(), 'token': serializers.CharField()},
        ),
        **DEFAULT_PRIVATE_API_ERRORS_SCHEMA_RESPONSES,
    },
)
class LoginView(KnoxLoginView):
    authentication_classes = [CustomBasicAuthentication]

    def post(self, request):
        response = super().post(request)
        response.set_cookie(key='Authorization', value=f"Token {response.data['token']}")
        return response


@extend_schema(
    tags=[AUTHENTIFICATION_SWAGGER_TAG],
    description='Верификация профиля по OTP коду',
    request=VerificationRequestSerializer,
    responses={
        status.HTTP_200_OK: SWAGGER_NO_RESPONSE_BODY,
        status.HTTP_404_NOT_FOUND: OpenApiResponse(
            response='User not found',
            examples=[OpenApiExample(name='User not found', value={'detail': 'user not found'})],
        ),
        **DEFAULT_PUBLIC_API_SCHEMA_RESPONSES,
    },
)
class ProfileVerificationView(APIView):
    """View, использующийся для верификации профиля пользователя по OTP коду"""

    def post(self, request, *args, **kwargs):
        serializer = VerificationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = make_phone_uniform(serializer.validated_data.get("phone"))
        otp = serializer.validated_data.get("otp_code")
        user = get_user_with_profile_by_phone(phone)
        profile = user.profile

        BaseVerificationService(user).verify_otp(otp)
        ProfileManagerService(profile).verify()

        return Response(status=status.HTTP_200_OK)


@extend_schema(
    tags=[AUTHENTIFICATION_SWAGGER_TAG],
    description='Отправить OTP код пользователю',
    request=PhoneSerializer,
    responses={
        status.HTTP_200_OK: SWAGGER_NO_RESPONSE_BODY,
        status.HTTP_404_NOT_FOUND: OpenApiResponse(
            response='User not found',
            examples=[OpenApiExample(name='User not found', value={'detail': 'user not found'})],
        ),
        **DEFAULT_PUBLIC_API_SCHEMA_RESPONSES,
    },
)
class SendVerificationCodeView(APIView):
    """View, использующийся для отправки OTP кода пользователю"""

    def post(self, request):
        serializer = PhoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = make_phone_uniform(serializer.validated_data.get("phone"))
        user = get_user_with_profile_by_phone(phone)
        otp = BaseVerificationService(user).create_otp()
        send_sms_task.delay(phone, MESSAGE_TEMPLATE.format(otp))

        return Response(status=status.HTTP_200_OK)


@extend_schema(
    tags=[AUTHENTIFICATION_SWAGGER_TAG],
    description='Валидация OTP кода',
    request=VerificationRequestSerializer,
    responses={
        status.HTTP_200_OK: SWAGGER_NO_RESPONSE_BODY,
        status.HTTP_404_NOT_FOUND: OpenApiResponse(
            response='User not found',
            examples=[OpenApiExample(name='User not found', value={'detail': 'user not found'})],
        ),
        **DEFAULT_PUBLIC_API_SCHEMA_RESPONSES,
    },
)
class ResetPasswordValidateTokenView(APIView):
    """View, использующийся для валидации OTP кода, без каких либо побочных эффектов"""

    def post(self, request: Request):
        serializer = VerificationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = make_phone_uniform(serializer.validated_data.get("phone"))
        user = get_user_with_profile_by_phone(phone)
        otp = serializer.validated_data.get("otp_code")

        BaseVerificationService(user).verify_otp(otp)

        return Response(status=status.HTTP_200_OK)


@extend_schema(
    tags=[AUTHENTIFICATION_SWAGGER_TAG],
    description='Смена пароля',
    request=PasswordResetSerializer,
    responses={
        status.HTTP_200_OK: SWAGGER_NO_RESPONSE_BODY,
        status.HTTP_404_NOT_FOUND: OpenApiResponse(
            response='User not found',
            examples=[OpenApiExample(name='User not found', value={'detail': 'user not found'})],
        ),
        **DEFAULT_PUBLIC_API_SCHEMA_RESPONSES,
    },
)
class ResetPasswordConfirmView(APIView):
    """View, использующийся для смены пароля"""

    def post(self, request: Request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = make_phone_uniform(serializer.validated_data.get("phone"))
        password = serializer.validated_data.get("password")
        otp = serializer.validated_data.get("otp_code")
        user = get_user_with_profile_by_phone(phone)

        BaseVerificationService(user).verify_otp(otp)
        PasswordManagerService(user).reset_password(new_password=password)

        return Response(status=status.HTTP_200_OK)


@extend_schema(
    tags=[AUTHENTIFICATION_SWAGGER_TAG],
    description='Зарегистрироваться',
    request=SignUpRequestSerializer,
    responses={
        status.HTTP_201_CREATED: inline_serializer(
            name='SignUpSerializer',
            fields={'profile': ProfileOwnerSerializer(), 'token': serializers.CharField()},
        ),
        **DEFAULT_PUBLIC_API_SCHEMA_RESPONSES,
    },
)
class SignUpView(APIView):
    def post(self, request: Request):
        serializer = SignUpRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        auth_token_val, auth_token_exp, profile = ProfileManagerService.create(**serializer.validated_data)
        serialized_profile = ProfileOwnerSerializer(profile).data

        response = Response(
            {"profile": serialized_profile, "token": {"token": auth_token_val, "expiry": auth_token_exp}},
            status=status.HTTP_201_CREATED,
        )
        response.set_cookie(key='Authorization', value=f"Token {auth_token_val}")

        return response


@extend_schema(tags=[PROFILE_SWAGGER_TAG])
class ProfileViewSet(ViewSet):
    permission_classes = [IsProfileOwnerOrReadOnly, IsAuthenticated]
    authentication_classes = [CookieTokenAuthentication]

    def get_permissions(self):
        if self.action in ("update", "destroy", "get_my_profile"):
            return super().get_permissions()
        return [AllowAny()]

    @extend_schema(
        description='Получить свой профиль',
        request={},
        responses={
            status.HTTP_200_OK: ProfileOwnerSerializer,
            **DEFAULT_PRIVATE_API_ERRORS_SCHEMA_RESPONSES,
        },
    )
    @action(detail=False, methods=['get'], url_path='my_profile')
    def get_my_profile(self, request: Request):
        profile = request.user.profile  # type: ignore
        serialized_profile = ProfileOwnerSerializer(profile).data

        return Response(serialized_profile, status=status.HTTP_200_OK)

    @extend_schema(
        description='Получить профиль пользователя с указанным id',
        request={},
        responses={
            status.HTTP_200_OK: ProfileSerializer,
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                response='Profile not found',
                examples=[OpenApiExample(name='Profile not found', value={'detail': 'profile not found'})],
            ),
            **DEFAULT_PRIVATE_API_ERRORS_SCHEMA_RESPONSES,
        },
    )
    def retrieve(self, request: Request, pk: int):
        profile = get_profile_with_user(pk)
        serialized_profile = ProfileSerializer(profile).data

        return Response(serialized_profile, status=status.HTTP_200_OK)

    @extend_schema(
        description='Обновить свой профиль',
        request=ProfileOwnerSerializer,
        responses={
            status.HTTP_200_OK: ProfileOwnerSerializer,
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                response='Profile not found',
                examples=[OpenApiExample(name='Profile not found', value={'detail': 'profile not found'})],
            ),
            **DEFAULT_PRIVATE_API_ERRORS_SCHEMA_RESPONSES,
        },
    )
    def update(self, request: Request, pk: int):
        profile = get_profile_with_user(pk)
        self.check_object_permissions(request, profile)

        serializer = ProfileOwnerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ProfileManagerService(profile).update(**serializer.validated_data)

        serialized_profile = ProfileOwnerSerializer(profile).data

        return Response(serialized_profile, status=status.HTTP_200_OK)

    @extend_schema(
        description='Удалить свой профиль',
        request={},
        responses={
            status.HTTP_204_NO_CONTENT: SWAGGER_NO_RESPONSE_BODY,
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                response='Profile not found',
                examples=[OpenApiExample(name='Profile not found', value={'detail': 'profile not found'})],
            ),
            **DEFAULT_PRIVATE_API_ERRORS_SCHEMA_RESPONSES,
        },
    )
    def destroy(self, request: Request, pk: int):
        profile = get_profile_with_user(pk)
        self.check_object_permissions(request, profile)

        ProfileManagerService(profile).soft_delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


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
