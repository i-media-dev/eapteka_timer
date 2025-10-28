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

cookies = {
    'spid': '1754565906295_bdfea2b738b6deab93c96c77274666c4_qjt13nc50oig59td',
    'BITRIX_SM_SALE_UID': '00a42701dba036ded8a3f1bbf6cbe7ae',
    '_ym_uid': '175456696059332069',
    '_ym_d': '1754566960',
    '_ymab_param': '6vSqNgZWJEqVVAhfvt3UcSyfpp2lTQ7OXYnFU5F1T5CnMJCaQQu9dUmGU37-vhaXxaDvmlvdbe70oVFj0Ip-3gPYQ6Y',
    'mindboxDeviceUUID': 'b78ef8c5-7fd8-4ade-9046-ae45dd0ecc32',
    'directCrm-session': '%7B%22deviceGuid%22%3A%22b78ef8c5-7fd8-4ade-9046-ae45dd0ecc32%22%7D',
    '_sa': 'SA1.1a86e677-84f3-4392-b4a9-dc7b209ed405.1754566960',
    'getExperimentsVarioqub': '%22P54lnS9LcLo%2C%22',
    'TILDAUTM': 'utm_medium%3Dcpc%7C%7C%7Cutm_campaign%3Dmsk-srch-hm-main-alt-other_test_purpose_new%7C%7C%7Cutm_source%3Dyandex%7C%7C%7Cutm_term%3D%25d1%2581%25d1%2582%25d0%25be%25d0%25bb%25d0%25b8%25d1%2587%25d0%25ba%25d0%25b8%2520%25d0%25bc%25d0%25be%25d1%2581%25d0%25ba%25d0%25b2%25d0%25b0%7C%7C%7Cutm_content%3D%7Cc%253a701071182%7Cg%253a5605343108%7Cb%253a17111033125%7Ck%253a55039425284%7Cst%253asearch%7Ca%253ano%7Cs%253anone%7Ct%253apremium%7Cp%253a1%7Cr%253a55039425284%7Cdev%253adesktop%7C%7C%7C',
    'spjs': '1761309325278_42cdc330_01350185_a2aae49ddb7b0f579815db4aee74d9e3_d0YDquJdbbCJVCTpTGwOPMfwgQfEGnuextIw9dy5Kb0V0KFUbJf2m6PfP9LqFncaIV2sUWmU9Zig3DhdhzFgYS2JnC01F4Lzvs9rv1cDJhJoocT4VU24pNx1Fo+C+zwxCf70aMAaybwEMKSw6NkJTWangmbOK3sq52Zs5Y3UdF0UjbgxKTbGqAytDlJ4HoQZDqorHUdAQLUNGQ/OpvICtk+rPj8iLHwgiEF1/PGNeFGKhqMacnq606gUo/bPmMk8FUT0JR1ab67TEra32qsbX3CM6WAYBZXcpH1Lp6qTdr0i35ozO4BwJLwoOWj1ARRQLrqqDjaThtf6ThSYpckMRWyydnpAWfixmPqU2E+8TZbzBVTR2dwsrHUAwvfPHB+r4pZXA34TAvmATCwRySRjTJc+zjL7E2fbws4v6MCVpWJ4jI7I0VMS5r4ry8+mkuSAjpNzuYEYKCQ8BCGPl6vbw5rQkv9m7T3tdEBh5C2YiTzm06RDW37/mhajfMC5dFRZIp4u80pXRVkBTHzwwJeV6A/bq31HEcLj+MzKzuYwsZVb//qpYU7P5KwF89+TvkkVWPXzL6PJuYGocnUTz5/IL4bTggM4jw/7ciYRVBjunsp1Gf13fZHATFQPjUUvYibNFSiLVl71ohcLba3YMET1YNj56f1UELUUrNgB+8U+HCAZhbVpUV6ukspGd9vjvy9zFPCAZFw96rklwoHCThoIHSez4nROt+Sb9im4FIxhEQmhvr5zqhYHvKC/OLzVcGHUfek5fKUC4iENXIiIgsdWg00gr1tTqphEfCDjq8ULiwPgVLdRYAtrMChb6tafmWAeFdsBZG2d2Zyk0D7Tixd2OxNfbHJIleecQf0c4MiVavgd+stvdwLCtp4aae3VgXE1LPjoXFQ/7EO59kb60p5eIgnVlUlxLNywiGQjx8+bWw8F8+L2vxloPXdRolRuS/s/cMyMcBiV1RpCji3xzZQ1OQjfXfBasYM5P0qq/OaiciYPeWn9RBDhNI5YJXvAn2wzCXbm+kMd6bGN1SH487nMksdS8ndumvi/1NMS9e4ZbT0AUKV0SbewnNGKC6TKkOY9AdosKUkE7DiQVSvv9pujFS8aCqoRRsdCiwvcKjOmVsN694BcEr6dkFwQs49W3+H+5ytbh7/kFE+U97JXPhJqzw5RIP1N6uG8BvE5Nd1xIA00yaggnRLDL1dKC2Hp9Ow4/tLbDpcQ7FLMCiX7kdPpNf/RqP3kr24yitb2+sqdnDIb2zVtahzNkcj0dWEo3T3+JtMCIDhPC24XcSJ0zTC4LIP+jkc94BDMRAwpZy+nhzuESks2HtFyEstPzooCwGCymz7vK4fS5CJrHnE5Rr39N46Uog1kCus3H2IW+6OvbjKE1CB0TBnp7RVBA2fJ3/4bUufjQA8E9bzkat2nOZRhPTQu+IJL1uD7tB847VWzpkFY/hzpBBSX46kt6lyh5jYQvUDkc0se/TOOWcoJ879uoouX8msjGM2p4QBEkN3ZaW2Th8Jzfl7L/5IGfOX48TW04s0O8loF9amRTTzk7QTHmY/To39fGuKuj1Io/YsREZWN2ajcxNfns8SY2QUy5m4aCfUtcUkU7DFgVSI3R5tzNwb6ov5OneZCdWAA1UyZyWwTz79jWwb2qoJePfHJlWU5ANyscEoT9xFP2TvfxhpqOQIpWHaZWmD1AcKKu+K+b7sC2amKsxL0fKmErSY/DB2Qp1o+SNSHKj+JMqPVBilCjSuQnzRzV9wLodot0qoWRzogXbl/iSHrSJX8i3/Gk2K3DNqo/kAxQWuH4Vy9nTn2oC1bqO8WEGIv0Tu27BGRauVO1KLYQ=',
    'spsc': '1761309325278_9306895ae1ec3c462892339378f6d7e8_vHRc54px3ivx2Nog.9C.ZEJ7mrTrYP6JKvyu482-.7B-g899L1gfAPsCI0zLM4j-Z',
    'PHPSESSID': 'lH3jG5WLiHh9EC73PAWejjOaGHZpu1ww',
    'regionId': '672',
    'PREVIOUS_STORE_ID': '6',
    '_ym_isad': '2',
    'BITRIX_SM_OAUTH_CITY_CODE': '%7B%22code%22%3A%22msc%22%2C%22ts%22%3A1761309780%7D',
}

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    'Referer': 'https://www.eapteka.ru/?utm_referrer=https%3a%2f%2fwww.google.com%2f',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    # 'Cookie': 'spid=1754565906295_bdfea2b738b6deab93c96c77274666c4_qjt13nc50oig59td; BITRIX_SM_SALE_UID=00a42701dba036ded8a3f1bbf6cbe7ae; _ym_uid=175456696059332069; _ym_d=1754566960; _ymab_param=6vSqNgZWJEqVVAhfvt3UcSyfpp2lTQ7OXYnFU5F1T5CnMJCaQQu9dUmGU37-vhaXxaDvmlvdbe70oVFj0Ip-3gPYQ6Y; mindboxDeviceUUID=b78ef8c5-7fd8-4ade-9046-ae45dd0ecc32; directCrm-session=%7B%22deviceGuid%22%3A%22b78ef8c5-7fd8-4ade-9046-ae45dd0ecc32%22%7D; _sa=SA1.1a86e677-84f3-4392-b4a9-dc7b209ed405.1754566960; getExperimentsVarioqub=%22P54lnS9LcLo%2C%22; TILDAUTM=utm_medium%3Dcpc%7C%7C%7Cutm_campaign%3Dmsk-srch-hm-main-alt-other_test_purpose_new%7C%7C%7Cutm_source%3Dyandex%7C%7C%7Cutm_term%3D%25d1%2581%25d1%2582%25d0%25be%25d0%25bb%25d0%25b8%25d1%2587%25d0%25ba%25d0%25b8%2520%25d0%25bc%25d0%25be%25d1%2581%25d0%25ba%25d0%25b2%25d0%25b0%7C%7C%7Cutm_content%3D%7Cc%253a701071182%7Cg%253a5605343108%7Cb%253a17111033125%7Ck%253a55039425284%7Cst%253asearch%7Ca%253ano%7Cs%253anone%7Ct%253apremium%7Cp%253a1%7Cr%253a55039425284%7Cdev%253adesktop%7C%7C%7C; spjs=1761309325278_42cdc330_01350185_a2aae49ddb7b0f579815db4aee74d9e3_d0YDquJdbbCJVCTpTGwOPMfwgQfEGnuextIw9dy5Kb0V0KFUbJf2m6PfP9LqFncaIV2sUWmU9Zig3DhdhzFgYS2JnC01F4Lzvs9rv1cDJhJoocT4VU24pNx1Fo+C+zwxCf70aMAaybwEMKSw6NkJTWangmbOK3sq52Zs5Y3UdF0UjbgxKTbGqAytDlJ4HoQZDqorHUdAQLUNGQ/OpvICtk+rPj8iLHwgiEF1/PGNeFGKhqMacnq606gUo/bPmMk8FUT0JR1ab67TEra32qsbX3CM6WAYBZXcpH1Lp6qTdr0i35ozO4BwJLwoOWj1ARRQLrqqDjaThtf6ThSYpckMRWyydnpAWfixmPqU2E+8TZbzBVTR2dwsrHUAwvfPHB+r4pZXA34TAvmATCwRySRjTJc+zjL7E2fbws4v6MCVpWJ4jI7I0VMS5r4ry8+mkuSAjpNzuYEYKCQ8BCGPl6vbw5rQkv9m7T3tdEBh5C2YiTzm06RDW37/mhajfMC5dFRZIp4u80pXRVkBTHzwwJeV6A/bq31HEcLj+MzKzuYwsZVb//qpYU7P5KwF89+TvkkVWPXzL6PJuYGocnUTz5/IL4bTggM4jw/7ciYRVBjunsp1Gf13fZHATFQPjUUvYibNFSiLVl71ohcLba3YMET1YNj56f1UELUUrNgB+8U+HCAZhbVpUV6ukspGd9vjvy9zFPCAZFw96rklwoHCThoIHSez4nROt+Sb9im4FIxhEQmhvr5zqhYHvKC/OLzVcGHUfek5fKUC4iENXIiIgsdWg00gr1tTqphEfCDjq8ULiwPgVLdRYAtrMChb6tafmWAeFdsBZG2d2Zyk0D7Tixd2OxNfbHJIleecQf0c4MiVavgd+stvdwLCtp4aae3VgXE1LPjoXFQ/7EO59kb60p5eIgnVlUlxLNywiGQjx8+bWw8F8+L2vxloPXdRolRuS/s/cMyMcBiV1RpCji3xzZQ1OQjfXfBasYM5P0qq/OaiciYPeWn9RBDhNI5YJXvAn2wzCXbm+kMd6bGN1SH487nMksdS8ndumvi/1NMS9e4ZbT0AUKV0SbewnNGKC6TKkOY9AdosKUkE7DiQVSvv9pujFS8aCqoRRsdCiwvcKjOmVsN694BcEr6dkFwQs49W3+H+5ytbh7/kFE+U97JXPhJqzw5RIP1N6uG8BvE5Nd1xIA00yaggnRLDL1dKC2Hp9Ow4/tLbDpcQ7FLMCiX7kdPpNf/RqP3kr24yitb2+sqdnDIb2zVtahzNkcj0dWEo3T3+JtMCIDhPC24XcSJ0zTC4LIP+jkc94BDMRAwpZy+nhzuESks2HtFyEstPzooCwGCymz7vK4fS5CJrHnE5Rr39N46Uog1kCus3H2IW+6OvbjKE1CB0TBnp7RVBA2fJ3/4bUufjQA8E9bzkat2nOZRhPTQu+IJL1uD7tB847VWzpkFY/hzpBBSX46kt6lyh5jYQvUDkc0se/TOOWcoJ879uoouX8msjGM2p4QBEkN3ZaW2Th8Jzfl7L/5IGfOX48TW04s0O8loF9amRTTzk7QTHmY/To39fGuKuj1Io/YsREZWN2ajcxNfns8SY2QUy5m4aCfUtcUkU7DFgVSI3R5tzNwb6ov5OneZCdWAA1UyZyWwTz79jWwb2qoJePfHJlWU5ANyscEoT9xFP2TvfxhpqOQIpWHaZWmD1AcKKu+K+b7sC2amKsxL0fKmErSY/DB2Qp1o+SNSHKj+JMqPVBilCjSuQnzRzV9wLodot0qoWRzogXbl/iSHrSJX8i3/Gk2K3DNqo/kAxQWuH4Vy9nTn2oC1bqO8WEGIv0Tu27BGRauVO1KLYQ=; spsc=1761309325278_9306895ae1ec3c462892339378f6d7e8_vHRc54px3ivx2Nog.9C.ZEJ7mrTrYP6JKvyu482-.7B-g899L1gfAPsCI0zLM4j-Z; PHPSESSID=lH3jG5WLiHh9EC73PAWejjOaGHZpu1ww; regionId=672; PREVIOUS_STORE_ID=6; _ym_isad=2; BITRIX_SM_OAUTH_CITY_CODE=%7B%22code%22%3A%22msc%22%2C%22ts%22%3A1761309780%7D',
}

# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
#     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
#     'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
#     'Accept-Encoding': 'gzip, deflate, br',
#     'Connection': 'keep-alive',
#     'Upgrade-Insecure-Requests': '1',
#     'Cache-Control': 'no-cache',
#     'Pragma': 'no-cache',
#     'Sec-Fetch-Dest': 'document',
#     'Sec-Fetch-Mode': 'navigate',
#     'Sec-Fetch-Site': 'none',
#     'Sec-Fetch-User': '?1',
#     'Cache-Control': 'max-age=0',
#     'Content-Type': 'application/json',
#     'Origin': 'https://www.eapteka.ru'
# }
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
    # print(response_add.status_code)

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
        timeout=10,
        cookies=cookies
    )
    # time.sleep(1)
    print(response_main.status_code)
    print(response_main.content)
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
                    f'превысило критический максимум - {result_time_cart} сек!'
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
                    f'максимум -  {result_time_main} сек!')
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
