from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_duration_seconds(value):
    if value.total_seconds() > 120:
        raise ValidationError(_('Duration cannot exceed 120 seconds.'))


def validate_periodicity_days(value):
    if value > 7:
        raise ValidationError(_('Periodicity cannot be more than 7 days.'))
