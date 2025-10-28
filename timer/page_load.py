import logging
import time
from pathlib import Path

from playwright.async_api import async_playwright

from timer.logging_config import setup_logging
from timer.constants import JS_CODE

setup_logging()


async def measure_main_page_load_time(url: str, output_file: str):
    async with async_playwright() as p:
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

        await browser.close()
