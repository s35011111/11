# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from .validators import validate_duration_seconds, validate_periodicity_days


class CustomUser(AbstractUser):
    telegram_chat_id = models.CharField(max_length=100,
                                        blank=True, null=True,
                                        unique=True)


class Habit(models.Model):
    HABIT_TYPES = [
        ('полезная', 'Полезная'),
        ('приятная', 'Приятная'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                             related_name='habits')
    place = models.CharField(max_length=255, blank=True)
    action = models.CharField(max_length=255)
    habit_type = models.CharField(max_length=10, choices=HABIT_TYPES)


    connected_habit = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'habit_type': 'полезная'},
        related_name='connected_from'
    )


    reward = models.CharField(max_length=255, blank=True, null=True)

    start_time = models.DateTimeField()
    duration = models.DurationField(
        validators=[validate_duration_seconds],
        help_text="maximum 120 seconds"
    )
    periodicity = models.PositiveIntegerField(
        validators=[validate_periodicity_days, MaxValueValidator(7)],
        help_text="Frequency in days (1–7)"
    )

    is_public = models.BooleanField(default=False)
    next_reminder = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Habit'
        verbose_name_plural = 'Habits'
        ordering = ['-start_time']

    def clean(self):


        if self.habit_type == 'useful' and not (self.reward
                                                or self.connected_habit):
            raise ValidationError(
                {'reward': 'If useful required reward or connected habit'
                           })


        if self.habit_type == 'pleasant':
            if self.reward:
                raise ValidationError(
                    {'reward': 'If pleasant then no reward'})
            if self.connected_habit:
                raise ValidationError(
                    {'connected_habit': 'If pleasant then no  connected habit'
                     })

        if self.connected_habit:
            if self.connected_habit.user != self.user:
                raise ValidationError(
                    {'connected_habit': 'Same owner for both habits'
                     })
            if self.connected_habit.habit_type != 'pleasant':
                raise ValidationError(
                    {'connected_habit': 'Connected habit must be a pleasant'
                     })


        if self.habit_type == 'useful':
            has_reward = bool(self.reward)
            has_connected = bool(self.connected_habit)

            if has_reward and has_connected:
                raise ValidationError(
                    'cant have both a reward and a connected habit'
                    'Choose one or the other.'
                )
            if not has_reward and not has_connected:
                raise ValidationError(
                    'must have either a reward or a connected habit'
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.action} ({self.habit_type})"
