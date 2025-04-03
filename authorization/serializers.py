import re

from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class PasswordValidator:
    """Класс для валидации пароля по заданным правилам."""

    SPECIAL_CHARS = r"!@#$%^&*(),.?\":{}|<>"

    @staticmethod
    def validate(password):
        if len(password) < 8:
            raise serializers.ValidationError("Пароль должен содержать минимум 8 символов.")
        if not any(char.isupper() for char in password):
            raise serializers.ValidationError("Пароль должен содержать минимум одну заглавную букву.")
        if not any(char.islower() for char in password):
            raise serializers.ValidationError("Пароль должен содержать минимум одну строчную букву.")
        if not any(char.isdigit() for char in password):
            raise serializers.ValidationError("Пароль должен содержать минимум одну цифру.")
        if not re.search(f"[{re.escape(PasswordValidator.SPECIAL_CHARS)}]", password):
            raise serializers.ValidationError("Пароль должен содержать минимум один спецсимвол (!@#$%^&*).")

class RegisterSerializer(serializers.ModelSerializer):
    email_code = serializers.CharField(max_length=6, write_only=True)
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    confirm_password = serializers.CharField(max_length=68, min_length=6, write_only=True)

    class Meta:
        model = User
        fields = ['email_code', 'email', 'first_name', 'last_name', 'username', 'password', 'confirm_password']

    def validate(self, attrs):
        user_email = attrs.get('email')
        if User.objects.filter(email=user_email):
            raise serializers.ValidationError("Пользователь с такой почтой уже зарегистрирован")

        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")

        if password != confirm_password:
            raise serializers.ValidationError("Пароли не совпадают")

        PasswordValidator.validate(password)

        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        validated_data.pop('email_code')
        user = User.objects.create_user(**validated_data)
        return user


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['email'] = self.user.email
        data['first_name'] = self.user.first_name
        data['last_name'] = self.user.last_name
        data["avatar_url"] = "https://static.tildacdn.com/tild6161-3439-4135-b561-636566633936/ssfLXmNqOus0BCy_EWsd.jpg"
        return data

    def get_token(self, user):
        token = super().get_token(user)
        token['email'] = user.email
        return token


class SendCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
