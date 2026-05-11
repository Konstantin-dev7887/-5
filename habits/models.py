from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Habit(models.Model):
    """Модель привычки."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='habits'
    )
    place = models.CharField(max_length=255, verbose_name='Место')
    time = models.TimeField(verbose_name='Время')
    action = models.CharField(max_length=255, verbose_name='Действие')

    is_pleasant = models.BooleanField(
        default=False,
        verbose_name='Приятная привычка'
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name='Публичная'
    )

    related_habit = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Связанная привычка',
        limit_choices_to={'is_pleasant': True}
    )
    reward = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Вознаграждение'
    )

    duration = models.PositiveIntegerField(
        default=120,
        verbose_name='Время на выполнение (сек)',
        validators=[MaxValueValidator(120)]
    )
    periodicity = models.PositiveIntegerField(
        default=1,
        verbose_name='Периодичность (дни)',
        validators=[MinValueValidator(1), MaxValueValidator(7)]
    )

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Создана')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлена')
    last_reminded = models.DateTimeField(
        blank=True, null=True, verbose_name='Последнее напоминание')

    def __str__(self):
        return f"{self.user}: {self.action} в {self.time} в {self.place}"

    class Meta:
        verbose_name = 'Привычка'
        verbose_name_plural = 'Привычки'
        ordering = ['-created_at']
