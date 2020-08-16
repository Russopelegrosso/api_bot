import logging
import os
import requests
import telegram
import time
from dotenv import load_dotenv
from requests import RequestException

load_dotenv()

PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
bot = telegram.Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):
    try:
        homework_name = homework['homework_name']
        homework_status = homework['status']
        if homework_status == 'rejected':
            verdict = 'К сожалению в работе нашлись ошибки.'
        elif homework_status == 'approved':
            verdict = ('Ревьюеру всё понравилось, '
                       'можно приступать к следующему уроку.')
        else:
            raise Exception('Status does not contain '
                            'value "rejected" or "approved"')
        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'
    except ValueError as err:
        logging.debug(err, 'Error getting "homework" values')


def get_homework_statuses(current_timestamp):
    if current_timestamp is None:
        raise ValueError('current_timestamp is None')
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    params = {
        'from_date': current_timestamp
    }
    try:
        homework_statuses = requests.get(url=URL,
                                         headers=headers,
                                         params=params)
        return homework_statuses.json()
    except RequestException as err:
        logging.debug(err, '"Error getting JSON"')


def send_message(message):
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())
    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(
                    parse_homework_status(new_homework.get('homeworks')[0]))
            current_timestamp = new_homework.get(
                'current_date')
            time.sleep(300)

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()
