import logging
import time
from datetime import datetime as dt
from pathlib import Path

from playwright.async_api import async_playwright

from timer.constants import (ADDRESS, CREATE_REPORTS_MODEL, DATE_FORMAT,
                             INSERT_REPORT, JS_CODE, TABLE_NAME, TIME_FORMAT)
from timer.decorators import connection_db
from timer.logging_config import setup_logging

setup_logging()


@connection_db
async def measure_main_page_load_time(url: str, output_file: str, cursor=None):
    async with async_playwright() as p:
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

        start_total = time.perf_counter()

        try:
            await page.goto(url, wait_until='load', timeout=60000)
            load_time = time.perf_counter() - start_total
            logging.info('Основная загрузка (load): %s с', round(load_time, 2))
            images_start = time.perf_counter()

            try:
                await page.wait_for_function(JS_CODE, timeout=10000)
                images_time = time.perf_counter() - images_start
                logging.info(
                    'Все изображения загружены: %s с',
                    round(images_time, 2)
                )
            except Exception as error:
                images_time = time.perf_counter() - images_start
                logging.warning(
                    'Не все изображения загрузились за %s с: %s',
                    round(images_time, 2),
                    error
                )
        except Exception as error:
            logging.error(
                'Страница не смогла загрузится за отведенное время: %s',
                error
            )

        total_time = time.perf_counter() - start_total
        logging.info(
            'ОБЩЕЕ ВРЕМЯ ЗАГРУЗКИ %s: %s с',
            output_file,
            round(total_time, 2)
        )

        html = await page.content()
        files_path = Path('media') / Path(output_file.split('_')[0])
        html_file = f'{output_file}.html'
        html_file_path = files_path / html_file
        files_path.mkdir(parents=True, exist_ok=True)
        with open(html_file_path, 'w', encoding='utf-8') as f:
            f.write(html)
        logging.info('HTML сохранён → %s', html_file_path)

        png_file = f'{output_file}.png'
        png_file_path = files_path / png_file
        await page.screenshot(path=png_file_path, full_page=True)
        logging.info('Скриншот сохранён → %s', png_file_path)

        if TABLE_NAME in tables_list:
            logging.info('Таблица %s найдена в базе', TABLE_NAME)
        else:
            create_table_query = CREATE_REPORTS_MODEL.format(
                table_name=TABLE_NAME
            )
            cursor.execute(create_table_query)
            logging.info('Таблица %s успешно создана', TABLE_NAME)

        page_name = output_file.split('_')[1]

        query = INSERT_REPORT.format(table_name=TABLE_NAME)
        params = [(
            date_str,
            time_str,
            url,
            page_name,
            total_time,
            f'{ADDRESS}{output_file}'
        )]
        cursor.executemany(query, params)
        logging.info('Данные сохранены')

        await browser.close()
