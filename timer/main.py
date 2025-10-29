import asyncio

from timer.constants import PHARMACIES
from timer.decorators import time_of_script
from timer.page_load import measure_main_page_load_time


@time_of_script
def main():
    async def run_all_measurements():
        tasks = []

        for pharmacy in PHARMACIES:
            output_file_main = f'{pharmacy}_main'
            output_file_cart = f'{pharmacy}_cart'
            url_main, url_cart = PHARMACIES[pharmacy]

            tasks.append(measure_main_page_load_time(
                url_main, output_file_main))
            tasks.append(measure_main_page_load_time(
                url_cart, output_file_cart))

        await asyncio.gather(*tasks)

    asyncio.run(run_all_measurements())


if __name__ == '__main__':
    main()
