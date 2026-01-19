import datetime

from django.conf import settings
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError


def validate_year(value):
    """Проверка, что год выпуска не больше текущего."""
    current_year = datetime.date.today().year
    if value > current_year:
        raise ValidationError(
            f'Год выпуска {value}'
            f'не может быть больше текущего {current_year}!'
        )


def validate_username_restricted(value):
    """Проверка, что имя пользователя не входит в список запрещенных."""
    if value in settings.FORBIDDEN_USERNAMES:
        raise ValidationError(
            f'Использовать имя "{value}" в качестве логина запрещено.'
        )


unicode_validator = UnicodeUsernameValidator()
