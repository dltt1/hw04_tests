import datetime


def year(request):
    """Добавляет переменную с текущим годом."""
    now = datetime.datetime.today()
    return {
        'year': now.year
    }
