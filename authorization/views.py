import random
import string

from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage

from django.template.loader import render_to_string
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from api.responses import bad_request_response
from modeling_system_backend import settings
from .models import EmailVerificationCode
from .serializers import RegisterSerializer, EmailTokenObtainPairSerializer, SendCodeSerializer

User = get_user_model()


class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        email = data.get('email')
        email_code = data.get('email_code')

        verification_entry = EmailVerificationCode.objects.filter(email=email).order_by("-created_at").first()

        if not verification_entry or not verification_entry.is_not_expired() or verification_entry.code != email_code:
            return bad_request_response('Неверный или просроченный код подтверждения.')

        serializer = RegisterSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            verification_entry.delete()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        error_list = []
        for key, error_message in dict(serializer.errors):
            error_list.append(error_message)
        error_message = ", ".join(error_list)
        return bad_request_response(error_message)


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer


class SendCodeView(generics.GenericAPIView):
    serializer_class = SendCodeSerializer

    def post(self, request, *args, **kwargs):
        user_email = request.data.get("email")

        existing_email = self.validate_email(user_email)
        if existing_email:
            return bad_request_response(existing_email)

        is_not_expired = self.is_not_expired(user_email)
        if is_not_expired:
            return Response({"wait_time": is_not_expired}, status=status.HTTP_200_OK)

        send_error = self.send_verification_code(user_email)
        if send_error:
            return bad_request_response(send_error)
        return Response(status=status.HTTP_200_OK)

    @staticmethod
    def validate_email(user_email):
        existing_email = User.objects.filter(email=user_email)
        if existing_email:
            return "Пользователь с такой почтой уже зарегистрирован"

    @staticmethod
    def generate_code(length=6):
        """Генерация случайного кода из цифр и букв."""
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))

    @staticmethod
    def is_not_expired(user_email):
        existing_code = EmailVerificationCode.objects.filter(email=user_email).first()
        if existing_code and existing_code.is_not_expired():
            return existing_code.is_not_expired()

    def send_verification_code(self, user_email):
        EmailVerificationCode.clean_expired_codes()

        verification_code = self.generate_code()

        subject = 'Подтверждение Email'

        site_host = settings.SITE_HOST
        message_context = {
            "confirmation_code": verification_code,
            "site_host": site_host
        }
        message = render_to_string("email_template.html", context=message_context)
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user_email]

        confirm_email = EmailMessage(subject, message, from_email=from_email, to=recipient_list)
        confirm_email.content_subtype = "html"
        try:
            confirm_email.send()
        except BaseException:
            return "Ошибка при отправке кода"

        EmailVerificationCode.objects.create(
            email=user_email,
            code=verification_code,
        )
