from drf_spectacular.utils import OpenApiResponse
from rest_framework import status

from typing import Dict

AUTH_ERRORS_SCHEMA_RESPONSES: Dict[int, OpenApiResponse] = {
    status.HTTP_401_UNAUTHORIZED: OpenApiResponse(description='Unauthorized'),
    status.HTTP_403_FORBIDDEN: OpenApiResponse(description='Forbidden'),
}

NOT_FOUND_ERROR_SCHEMA_RESPONSES: Dict[int, OpenApiResponse] = {
    status.HTTP_404_NOT_FOUND: OpenApiResponse(description='Not Found'),
}

REQUEST_ERRORS_SCHEMA_RESPONSES: Dict[int, OpenApiResponse] = {
    status.HTTP_400_BAD_REQUEST: OpenApiResponse(description='Bad Request'),
    status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description='Internal Server Error'),
}

DEFAULT_ERRORS_SCHEMA_RESPONSES: Dict[int, OpenApiResponse] = {
    **AUTH_ERRORS_SCHEMA_RESPONSES,
    **REQUEST_ERRORS_SCHEMA_RESPONSES,
}

DEFAULT_ERRORS_WITH_404_SCHEMA_RESPONSES: Dict[int, OpenApiResponse] = {
    **DEFAULT_ERRORS_SCHEMA_RESPONSES,
    **NOT_FOUND_ERROR_SCHEMA_RESPONSES,
}
