import datetime as dt
from django.core.exceptions import ValidationError

CHECK_YEAR = 'Проверьте год выпуска произведения'


def validate_year(value):
    year = dt.date.today().year
    if year < value:
        raise ValidationError(CHECK_YEAR)
    return value
