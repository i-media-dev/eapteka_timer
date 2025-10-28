import asyncio

from timer.page_load import measure_main_page_load_time
from timer.constants import PHARMACIES
from timer.decorators import time_of_script


@time_of_script
def main():
    for pharmacy in PHARMACIES:
        output_file_main = f'{pharmacy}_main'
        output_file_cart = f'{pharmacy}_cart'
        url_main, url_cart = PHARMACIES[pharmacy]
        asyncio.run(measure_main_page_load_time(url_main, output_file_main))
        asyncio.run(measure_main_page_load_time(url_cart, output_file_cart))


if __name__ == '__main__':
    main()
