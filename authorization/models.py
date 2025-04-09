from django.db import models
from django.utils import timezone
from datetime import timedelta

class EmailVerificationCode(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_not_expired(self):
        """Проверка, истек ли срок действия кода (5 минут)."""
        expiration_time = self.created_at + timedelta(minutes=5)
        remaining_time = (expiration_time - timezone.now()).total_seconds()

        return max(0, int(remaining_time)) if remaining_time > 0 else False

    def is_not_allow_new_code(self):
        allow_new_code = self.created_at + timedelta(minutes=1)
        remaining_time = (allow_new_code - timezone.now()).total_seconds()
        return max(0, int(remaining_time)) if remaining_time > 0 else False

    @classmethod
    def clean_expired_codes(cls):
        """Очищает все истекшие коды подтверждения."""
        cls.objects.filter(created_at__lt=timezone.now() - timedelta(minutes=5)).delete()

    def __str__(self):
        return f"Code for {self.email}"

    class Meta:
        verbose_name = 'Код подтверждения электронной почты'
        verbose_name_plural = 'Коды подтверждения электронной почты'
