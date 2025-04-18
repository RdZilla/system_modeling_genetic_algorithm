import os

from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics, status
from rest_framework.response import Response

from api.responses import success_response, bad_request_response, not_found_response, no_content_response
from api.statuses import SCHEMA_GET_POST_STATUSES, SCHEMA_PERMISSION_DENIED, STATUS_204, \
    SCHEMA_RETRIEVE_UPDATE_DESTROY_STATUSES
from api.utils.load_custom_funcs.UserFunctionMixin import UserFunctionMixin
from api.utils.load_custom_funcs.core_function_utils import SUPPORTED_MODELS_GA
from api.utils.load_custom_funcs.load_custom_functions import extract_kwargs_params_from_module_path
from task_modeling.serializers import MathFunctionsSerializer


class MathFunctionsView(generics.GenericAPIView, UserFunctionMixin):
    serializer_class = MathFunctionsSerializer

    @extend_schema(
        tags=["Math Functions"],
        summary="Get math functions",
        description="Get math functions",
        responses={
            status.HTTP_200_OK: MathFunctionsSerializer,
            **SCHEMA_GET_POST_STATUSES,
            **SCHEMA_PERMISSION_DENIED
        }
    )
    def get(self, request, *args, **kwargs):
        user = self.request.user
        user_id = user.id
        functions_mapping = self.get_functions_mapping(user_id)
        if isinstance(functions_mapping, Response):
            return functions_mapping

        keys = [
            "adaptation_functions",
            "crossover_functions",
            "fitness_functions",
            "initialize_population_functions",
            "mutation_functions",
            "selection_functions",
            "termination_functions"
        ]

        response = {
            "supported_models": SUPPORTED_MODELS_GA.keys(),
        }

        for key, function_mapping in zip(keys, functions_mapping):
            function_response = {}
            for function_name, function_path in function_mapping.items():
                function_kwargs = extract_kwargs_params_from_module_path(function_path)
                function_response[function_name] = function_kwargs
            response[key] = function_response

        return Response(response, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id='upload_files',
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'function_py_file': {
                        'type': 'string',
                        'format': 'binary'
                    }
                }
            }
        },

        tags=["Math Functions"],
        summary="Create math function",
        parameters=[
            OpenApiParameter(
                name="type_of_function", type=str, description='Выберите функцию файла',
                required=True, enum=["adaptation", "crossover", "fitness", "initialize_population_functions", "mutation",
                                     "selection", "termination"]
            )
        ],
        description="Create math function",
        responses={
            status.HTTP_200_OK: MathFunctionsSerializer,
            **SCHEMA_GET_POST_STATUSES,
            **SCHEMA_PERMISSION_DENIED
        }
    )
    def post(self, request, *args, **kwargs):
        user = self.request.user
        user_id = user.id
        type_of_function = request.query_params.get("type_of_function")

        user_function_folder = self.get_user_function_folder(type_of_function, user_id)
        if isinstance(user_function_folder, Response):
            return user_function_folder

        function_file = request.data.get("function_py_file")

        serializer = MathFunctionsSerializer(data={"function_file": function_file})
        if not serializer.is_valid():
            return bad_request_response("Data is not valid")

        uploaded_file = serializer.validated_data['function_file']
        file_name = uploaded_file.name
        file_path = os.path.join(user_function_folder, file_name)
        if os.path.exists(file_path):
            return bad_request_response(f"File {file_name} already exists")

        with open(file_path, 'wb') as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)

        return success_response("The file was uploaded successfully")

    @extend_schema(
        tags=['Math Functions'],
        summary="Delete math function",
        parameters=[
            OpenApiParameter(
                name="type_of_function", type=str, description='Выберите функцию файла',
                required=True, enum=["adaptation", "crossover", "fitness", "initialize_population_functions", "mutation",
                                     "selection", "termination"]
            ),
            OpenApiParameter(name="function_name", type=str, description='Название файла (example: file_name.py)',
                             required=True),
        ],
        responses={
            **STATUS_204,
            **SCHEMA_RETRIEVE_UPDATE_DESTROY_STATUSES,
            **SCHEMA_PERMISSION_DENIED,
        }
    )
    def delete(self, request, *args, **kwargs):
        user = self.request.user
        user_id = user.id
        type_of_function = request.data.get("type_of_function")

        user_function_folder = self.get_user_function_folder(type_of_function, user_id)
        if isinstance(user_function_folder, Response):
            return user_function_folder

        function_name = request.data.get("function_name")
        if not function_name:
            return bad_request_response(f"Invalid value {function_name = }")
        file_path = os.path.join(user_function_folder, function_name)
        if os.path.exists(file_path):
            os.remove(file_path)
            return no_content_response(function_name)
        else:
            return not_found_response(f"function with {function_name = }")


class GetSupportedAlgorithmView(generics.GenericAPIView):
    @extend_schema(
        tags=["Math Functions"],
        summary="Get supported algorithms",
        description="Get info about supported algorithms",
        responses={
            status.HTTP_200_OK: MathFunctionsSerializer,
            **SCHEMA_GET_POST_STATUSES,
            **SCHEMA_PERMISSION_DENIED
        }
    )
    def get(self, request, *args, **kwargs):

        response = {}
        for model_name, model_class in SUPPORTED_MODELS_GA.items():
            response[model_name] = model_class.REQUIRED_PARAMS
        return Response(response, status=status.HTTP_200_OK)