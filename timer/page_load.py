import logging
import os
import time
from datetime import datetime as dt
from pathlib import Path

from playwright.async_api import async_playwright
from telebot import TeleBot

from timer.constants import (ADDRESS, ALERT_ROBOT, CLIENT_IDS,
                             CREATE_REPORTS_MODEL, DATE_FORMAT, INSERT_REPORT,
                             LIMIT_FOR_ALLERT, REDUCTION, REPEAT, STATUS_CODES,
                             TABLE_NAME, TIME_FORMAT, TIMEOUT_PAGE,
                             TIMEOUT_SCREENSHOT)
from timer.decorators import connection_db
from timer.logging_config import setup_logging

setup_logging()

eapteka_bot = TeleBot(os.getenv('EAPTEKA_TOKEN_TELEGRAM'))


def send_bot_message(
    url: str,
    status_code: int,
    load_time: float,
    screenshot: str
) -> None:

    # robot = CRY_ROBOT if page == 'main' else WAIT_ROBOT

    if status_code == 200:
        if load_time > LIMIT_FOR_ALLERT:
            try:
                for id in CLIENT_IDS:
                    # with open(robot, 'rb') as photo:
                    #     eapteka_bot.send_sticker(id, photo)
                    eapteka_bot.send_message(
                        chat_id=id,
                        text='Время ожидания ответа от сервера при загрузке '
                        f'страницы - {url} превысило критический '
                        f'максимум -  {load_time} сек!'
                        f'\nСкирншот страницы - {screenshot}'
                    )
                    logging.info(f'Сообщение отправлено пользователю {id}')
            except Exception as e:
                logging.error(f'Пользователь {id} недоступен: {e}')
    else:
        try:
            for id in CLIENT_IDS:
                with open(ALERT_ROBOT, 'rb') as photo:
                    eapteka_bot.send_sticker(id, photo)
                eapteka_bot.send_message(
                    chat_id=id,
                    text=f'При запросе на страницу - {url} сервер '
                    f'вернул код ответа: {status_code}. '
                    'Это значит: '
                    f'{STATUS_CODES.get(status_code, "Неизвестно")}'
                )
                logging.info(f'Сообщение отправлено пользователю {id}')
        except Exception as e:
            logging.error(f'Пользователь {id} недоступен: {e}')


@connection_db
async def measure_main_page_load_time(url: str, output_file: str, cursor=None):
    async with async_playwright() as p:
        attempt = 0
        repeat_times_list = []
        cursor.execute('SHOW TABLES')
        tables_list = [table[0] for table in cursor.fetchall()]

        date_str = dt.now().strftime(DATE_FORMAT)
        time_str = dt.now().strftime(TIME_FORMAT)

        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled"
            ]
        )

        user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/127.0.0.0 Safari/537.36"
        )
        headers = {
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": url,
        }

        context = await browser.new_context(
            user_agent=user_agent,
            viewport={'width': 1920, 'height': 1080},
            java_script_enabled=True,
        )
        await context.set_extra_http_headers(headers)
        page = await context.new_page()
        logging.info('Начало загрузки страницы %s', output_file)

        while attempt < REPEAT:

            await context.close()
            context = await browser.new_context(
                user_agent=user_agent,
                viewport={'width': 1920, 'height': 1080},
                java_script_enabled=True,
            )
            await context.set_extra_http_headers(headers)
            page = await context.new_page()

            attempt += 1
            try:
                start_total = time.perf_counter()
                response = await page.goto(
                    url,
                    wait_until='load',
                    timeout=TIMEOUT_PAGE
                )
                load_time = round(time.perf_counter() - start_total, 2)
                logging.info('Загрузка  завершена: %s с', round(load_time, 2))

            except Exception as error:
                logging.error(
                    'Страница %s не загрузилась за %s секунд: %s',
                    output_file,
                    TIMEOUT_PAGE / REDUCTION,
                    error
                )
                load_time = round(time.perf_counter() - start_total, 2)

            logging.info(
                '\nПопытка %s/%s'
                '\nОБЩЕЕ ВРЕМЯ ЗАГРУЗКИ %s: %s с',
                attempt,
                REPEAT,
                output_file,
                load_time
            )
            repeat_times_list.append(load_time)
        avg_time = round(sum(repeat_times_list) / len(repeat_times_list), 2)
        logging.info(
            '\nСреднее время загрузки страницы %s за %s попыток - %s',
            output_file,
            REPEAT,
            avg_time
        )
        try:
            html = await page.content()
        except Exception as error:
            logging.warning(
                'Редкая ошибка JS-скрипт начал какую-то '
                'навигацию не в тайминг: %s',
                error
            )
            await page.wait_for_timeout(TIMEOUT_SCREENSHOT)
            html = await page.content()

        files_path = Path('media') / Path(output_file.split('_')[0])
        html_file = f'{output_file}.html'
        html_file_path = files_path / html_file
        files_path.mkdir(parents=True, exist_ok=True)
        with open(html_file_path, 'w', encoding='utf-8') as f:
            f.write(html)
        logging.info('HTML сохранён → %s', html_file_path)

        hour_str = time_str.split(':')[0]
        png_file = f'{output_file}_{date_str}_{hour_str}.png'
        png_file_path = files_path / png_file
        await page.wait_for_timeout(TIMEOUT_SCREENSHOT)
        await page.screenshot(path=png_file_path, full_page=True)
        logging.info('Скриншот сохранён → %s', png_file_path)

        page_name = output_file.split('_')[1]
        status_code = response.status if response else 0
        screenshot = f'{ADDRESS}{output_file.split('_')[0]}/{png_file}'
        if 'eapteka' in output_file:
            send_bot_message(url, status_code, avg_time, screenshot)

        if TABLE_NAME in tables_list:
            logging.info('Таблица %s найдена в базе', TABLE_NAME)
        else:
            create_table_query = CREATE_REPORTS_MODEL.format(
                table_name=TABLE_NAME
            )
            cursor.execute(create_table_query)
            logging.info('Таблица %s успешно создана', TABLE_NAME)

        query = INSERT_REPORT.format(table_name=TABLE_NAME)
        params = [(
            date_str,
            time_str,
            url,
            page_name,
            avg_time,
            screenshot
        )]
        cursor.executemany(query, params)
        logging.info('Данные сохранены')

        await browser.close()
