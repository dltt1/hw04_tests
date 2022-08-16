from django.core.mail import send_mail

send_mail(
    'Тема письма',
    'Текст письма.',
    'from@example.com',  # Это поле "От кого"
    ['to@example.com'],  # Это поле "Кому" (можно указать список адресов)
    fail_silently=False  # Сообщать об ошибках («молчать ли об ошибках?»)
)
