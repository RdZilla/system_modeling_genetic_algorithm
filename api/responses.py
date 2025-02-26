from rest_framework import status
from rest_framework.response import Response

RESPONSE_KEY = "detail"


# 400
def bad_request_response(error_content):
    error_dict = {RESPONSE_KEY: error_content}
    error_status = status.HTTP_400_BAD_REQUEST
    return Response(error_dict, status=error_status)


# 404
def not_found_response(error_content):
    error_dict = {RESPONSE_KEY: f"Object {error_content} has not found"}
    error_status = status.HTTP_404_NOT_FOUND
    return Response(error_dict, status=error_status)


# 403
def permission_denied_response():
    error_dict = {RESPONSE_KEY: "Permission denied"}
    error_status = status.HTTP_403_FORBIDDEN
    return Response(error_dict, status=error_status)


# 409
def conflict_response(obj_id):
    error_dict = {RESPONSE_KEY: obj_id}
    error_status = status.HTTP_409_CONFLICT
    return Response(error_dict, status=error_status)


# 200
def success_response(success_content):
    success_dict = {RESPONSE_KEY: success_content}
    error_status = status.HTTP_200_OK
    return Response(success_dict, status=error_status)


# 201
def created_response(created_obj_id):
    created_dict = {RESPONSE_KEY: created_obj_id}
    created_status = status.HTTP_201_CREATED
    return Response(created_dict, status=created_status)


# 204
def no_content_response(delete_id):
    deleted_dict = {RESPONSE_KEY: delete_id}
    deleted_status = status.HTTP_204_NO_CONTENT
    return Response(deleted_dict, status=deleted_status)
