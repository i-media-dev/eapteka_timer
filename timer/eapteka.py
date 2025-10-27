import asyncio
from playwright.async_api import async_playwright
import time


async def measure_real_page_load_time(url: str, output_file: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"]
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
            viewport={"width": 1920, "height": 1080},
            java_script_enabled=True,
        )
        await context.set_extra_http_headers(headers)
        page = await context.new_page()

        start = time.perf_counter()
        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
        except Exception:
            start = time.perf_counter()
            print("networkidle не дождался — переключаемся на load")
            await page.goto(url, wait_until="load", timeout=60000)
        end = time.perf_counter()
        print(f"Время загрузки (по Playwright): {end - start:.2f} с")

        navigation_timing = await page.evaluate("""
        () => {
            const t = performance.timing;
            return t.loadEventEnd - t.navigationStart;
        }
        """)
        print(
            f"Время загрузки (по браузеру): {navigation_timing / 1000:.2f} с"
        )

        html = await page.content()
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"HTML сохранён → {output_file}")

        screenshot_file = output_file.rsplit(".", 1)[0] + ".png"
        await page.screenshot(path=screenshot_file, full_page=True)
        print(f"Скриншот сохранён → {screenshot_file}")

        await browser.close()


def main():
    url = "https://www.eapteka.ru/"
    # url = 'https://www.eapteka.ru/personal/cart/'
    output_file = "eapteka.html"
    asyncio.run(measure_real_page_load_time(url, output_file))


if __name__ == "__main__":
    main()
