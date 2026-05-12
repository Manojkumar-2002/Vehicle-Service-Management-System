from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from apps.common.utils.response_utils import ResponseHandler
from apps.common.utils.serializer_utils import SerializerErrorHandler


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return ResponseHandler.error_response(
                message=SerializerErrorHandler.get_first_error_message(serializer.errors),
                errors=SerializerErrorHandler.format_errors(serializer.errors),
                status_code=status.HTTP_400_BAD_REQUEST
            )

        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return ResponseHandler.success_response(
            "Registration successful",
            data={
                "user": UserSerializer(user).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status_code=status.HTTP_201_CREATED
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return ResponseHandler.error_response(
                message=SerializerErrorHandler.get_first_error_message(serializer.errors),
                errors=SerializerErrorHandler.format_errors(serializer.errors),
                status_code=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )
        if not user:
            return ResponseHandler.error_response(
                "Invalid credentials",
                status_code=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)
        return ResponseHandler.success_response(
            "Login successful",
            data={
                "user": UserSerializer(user).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }
        )


class UserDetailView(APIView):
    def get(self, request):
        return ResponseHandler.success_response(
            "User details fetched successfully",
            data=UserSerializer(request.user).data
        )