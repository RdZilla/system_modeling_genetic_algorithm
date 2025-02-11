from drf_spectacular.utils import inline_serializer
from rest_framework import serializers, status
from rest_framework.response import Response

# schemas permission denied for documentation
SCHEMA_PERMISSION_DENIED = {
    status.HTTP_401_UNAUTHORIZED: inline_serializer(
        "Unauthorized",
        {
            "detail": serializers.CharField(default="You do not have sufficient permissions to perform this action."),
        }
    ),
    status.HTTP_403_FORBIDDEN: inline_serializer(
        "Forbidden",
        {
            "detail_": serializers.CharField(default="Authentication credentials were not provided."),
        }
    )
}

STATUS_204 = {
    status.HTTP_204_NO_CONTENT: inline_serializer(
        "No Content",
        {
            "detail": serializers.CharField(default="No Content"),
        }
    )
}

STATUS_400 = {
    status.HTTP_400_BAD_REQUEST: inline_serializer(
        "Bad Request",
        {
            "detail": serializers.CharField(default="Bad Request"),
        }
    )
}

STATUS_404 = {
    status.HTTP_404_NOT_FOUND: inline_serializer(
        "Not Found",
        {
            "detail": serializers.CharField(default="Not Found"),
        }
    )
}

STATUS_500 = {
    status.HTTP_500_INTERNAL_SERVER_ERROR: inline_serializer(
        "Internal Server Error",
        {
            "detail": serializers.CharField(default="Internal Server Error"),
        }
    )
}

SCHEMA_GET_POST_STATUSES = {
    **STATUS_400,
    **STATUS_500
}

SCHEMA_RETRIEVE_UPDATE_DESTROY_STATUSES = {
    **STATUS_400,
    **STATUS_404,
    **STATUS_500
}

RESPONSE_STATUS_403 = Response(data={"detail": "У вас недостаточно прав для выполнения данного действия."},
                               status=status.HTTP_403_FORBIDDEN)