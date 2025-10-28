import os

from dotenv import load_dotenv

load_dotenv()

TIME_DELAY = 5
"""Время повторного реконнекта к дб в секундах."""

MAX_RETRIES = 5
"""Максимальное количество переподключений к бд."""

DATE_FORMAT = '%Y-%m-%d'
"""Формат даты по умолчанию."""

TIME_FORMAT = '%H:%M:%S'
"""Формат времени по умолчанию."""

PHARMACIES = {
    'eapteka': (
        'https://www.eapteka.ru/',
        'https://www.eapteka.ru/personal/cart/',
    ),
    'aptekaru': (
        'https://apteka.ru/',
        'https://apteka.ru/cart/',
    ),
    'stolichki': (
        'https://stolichki.ru/',
        'https://stolichki.ru/basket'
    ),
    'planetazdorovo': (
        'https://planetazdorovo.ru/',
        'https://planetazdorovo.ru/cart/',
    ),
    'zdorovru': (
        'https://zdorov.ru/',
        'https://zdorov.ru/order/basket',
    ),
    'gorzdrav': (
        'https://new.gorzdrav.org/',
        'https://new.gorzdrav.org/checkout/mixed/reservation/',
    )
}
"""Словарь всех сайтов с urls главной страницы и корзины."""

JS_CODE = """
    () => {
        const images = Array.from(document.images);
        if (images.length === 0) return true;

        const loadedCount = images.filter(img =>
            img.complete && img.naturalWidth > 0
        ).length;

        return loadedCount >= images.length * 0.7;
    }
"""
"""JS код проверки загруженныйх изображений."""

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
