import os

from dotenv import load_dotenv

load_dotenv()


ADDRESS = 'https://feeds.i-media.ru/scripts/eapteka_timer/media/'
"""Путь к файлу на ftp."""

TABLE_NAME = 'loading_reports'

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

    const networkImages = images.filter(img => {
        return true; // Пока берем все
    });

    if (networkImages.length === 0) return true;

    const loadedImages = networkImages.filter(img => {
        return img.complete &&
               img.naturalWidth > 0 &&
               img.naturalHeight > 0;
    });

    return loadedImages.length >= Math.max(1, networkImages.length * 0.5);
}
"""
"""JS код проверки загруженныйх изображений."""

LIMIT_FOR_ALLERT = 0.85
"""Верхний предел ожидания ответа от сервера."""

CLIENT_IDS = (os.getenv('GROUP_ID'),)
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

CREATE_REPORTS_MODEL = '''
CREATE TABLE IF NOT EXISTS {table_name} (
    `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `date` DATE NOT NULL,
    `time` TIME NOT NULL,
    `website` VARCHAR(255) NOT NULL,
    `page_name` VARCHAR(255) NOT NULL,
    `loading_time` DECIMAL(10,2) UNSIGNED NOT NULL,
    `screenshot` VARCHAR(500) NOT NULL,
    UNIQUE KEY `unique_{table_name}_combo` (`date`, `time`, `website`)
);
'''
"""Запрос на создание таблицы бд."""

INSERT_REPORT = '''
INSERT INTO {table_name} (
    date,
    time,
    website,
    page_name,
    loading_time,
    screenshot
)
VALUES (%s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE id = id
'''
