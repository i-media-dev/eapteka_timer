import logging
import os
import time
import uuid

from dotenv import load_dotenv
import requests
from telebot import TeleBot

from timer.constants import (
    CLIENT_IDS,
    LIMIT_FOR_ALLERT,
    STATUS_CODES,
    TEST_CODE_RESPONSE
)
from timer.logging_config import setup_logging

load_dotenv()
setup_logging()


url_cart = 'https://api.neon.click/api/v3/events/cart'
url_main = 'https://www.eapteka.ru/'

session_id = str(uuid.uuid4())

payload_add = {
    'city': 'msc',
    'key': 'HJD45GSF534',
    'neon_id': f'n3on:{str(uuid.uuid4())}',
    'session_id': session_id,
    'sku': 316452,
    'type': 'add'
}

payload_remove = {
    'city': 'msc',
    'id': 316452,
    'key': 'HJD45GSF534',
    'neon_id': f'n3on:{str(uuid.uuid4())}',
    'session_id': session_id,
    'sku': 316452,
    'type': 'minus'
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Cache-Control': 'max-age=0',
    'Content-Type': 'application/json',
    'Origin': 'https://www.eapteka.ru'
}
result_time_cart = 0.0
result_time_main = 0.0

start_time = time.time()
try:
    response_add = requests.post(
        url_cart,
        json=payload_add,
        headers=headers,
        timeout=10
    )
    # time.sleep(1)
    end_time = time.time()
    result_time_cart = round(end_time - start_time, 3)
    logging.info(f'Товар {payload_add['sku']} добавлен в корзину')

    if response_add.status_code == requests.codes.ok:
        logging.info(f'Время добавления в корзину: {result_time_cart} секунд')
    else:
        logging.warning(
            f'Сервер вернул код ответа: {response_add.status_code}'
        )

    response_remove = requests.post(
        url_cart,
        json=payload_remove,
        headers=headers,
        timeout=10
    )
    if response_remove.status_code == requests.codes.ok:
        logging.info(f'Товар {payload_remove['id']} удален из корзины')
    else:
        logging.warning(
            f'Сервер вернул код ответа: {response_remove.status_code}'
        )

    start_time = time.time()
    response_main = requests.get(
        url_main,
        headers=headers,
        timeout=10
    )
    # time.sleep(1)
    end_time = time.time()
    result_time_main = round(end_time - start_time, 3)

    if response_main.status_code == requests.codes.ok:
        logging.info(
            f'Время загрузки главной страницы: {result_time_main} секунд'
        )
    else:
        logging.warning(
            f'Сервер вернул код ответа: {response_main.status_code}'
        )

except requests.exceptions.Timeout:
    logging.warning('Таймаут соединения')
except requests.exceptions.ConnectionError:
    logging.error('Ошибка подключения')
except Exception as e:
    logging.error(f'Ошибка: {e}')

eapteka_token = os.getenv('EAPTEKA_TOKEN_TELEGRAM')

if not eapteka_token:
    logging.error('Токен отсутсвует или не действителен')

eapteka_bot = TeleBot(eapteka_token)

if response_add.status_code == requests.codes.ok:
    if result_time_cart > LIMIT_FOR_ALLERT:
        try:
            for id in CLIENT_IDS:
                with open('robot/wait-robot.png', 'rb') as photo:
                    eapteka_bot.send_sticker(id, photo)
                eapteka_bot.send_message(
                    chat_id=id,
                    text='Время обработки запроса добавления в корзину '
                    f'превысило критический максимум - {result_time_cart}!'
                )
        except Exception as e:
            logging.error(f'Пользователь {id} недоступен: {e}')
else:
    for id in CLIENT_IDS:
        with open('robot/alert-robot.png', 'rb') as photo:
            eapteka_bot.send_sticker(id, photo)
        eapteka_bot.send_message(
            chat_id=id,
            text='При запросе на добавление в корзину страницу сервер '
            f'вернул код ответа: {response_add.status_code}'
            'Это значит: '
            f'{STATUS_CODES.get(response_add.status_code, "Не известно")}'
        )


if response_main.status_code == requests.codes.ok:
    if result_time_main > LIMIT_FOR_ALLERT:
        try:
            for id in CLIENT_IDS:
                with open('robot/cry-robot.png', 'rb') as photo:
                    eapteka_bot.send_sticker(id, photo)
                eapteka_bot.send_message(
                    chat_id=id,
                    text='Время ожидания ответа от сервера при загрузке '
                    'главной страницы превысило критический '
                    f'максимум -  {result_time_main}!')
        except Exception as e:
            logging.error(f'Пользователь {id} недоступен: {e}')
else:
    for id in CLIENT_IDS:
        with open('robot/alert-robot.png', 'rb') as photo:
            eapteka_bot.send_sticker(id, photo)
        eapteka_bot.send_message(
            chat_id=id,
            text='При запросе на главную страницу сервер '
            f'вернул код ответа: {response_main.status_code}. '
            'Это значит: '
            f'{STATUS_CODES.get(response_main.status_code, "Не известно")}'
        )
