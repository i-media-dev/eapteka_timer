import os

from dotenv import load_dotenv

load_dotenv()

LIMIT_FOR_ALLERT = 0.85
"""Верхний предел ожидания ответа от сервера."""

CLIENT_IDS = (os.getenv('MY_ID'), os.getenv('GROUP_ID'))
"""Кортеж доступных id."""

STATUS_CODES = {
    # Успешные ответы
    200: 'OK - Успешный запрос',
    201: 'Created - Ресурс создан',
    202: 'Accepted - Запрос принят, но еще не обработан',
    204: 'No Content - Нет содержимого для возврата',

    # Перенаправления
    301: 'Moved Permanently - Постоянное перенаправление',
    302: 'Found - Временное перенаправление',
    304: 'Not Modified - Контент не изменился',

    # Ошибки клиента
    400: 'Bad Request - Неверный запрос',
    401: 'Unauthorized - Требуется аутентификация',
    403: 'Forbidden - Доступ запрещен',
    404: 'Not Found - Ресурс не найден',
    405: 'Method Not Allowed - Метод не разрешен',
    408: 'Request Timeout - Таймаут запроса',
    429: 'Too Many Requests - Слишком много запросов',

    # Ошибки сервера
    500: 'Internal Server Error - Внутренняя ошибка сервера',
    502: 'Bad Gateway - Плохой шлюз',
    503: 'Service Unavailable - Сервис недоступен',
    504: 'Gateway Timeout - Таймаут шлюза',
}
"""Словарь кодов ответов от сервера и их значения."""

TEST_CODE_RESPONSE = 403
