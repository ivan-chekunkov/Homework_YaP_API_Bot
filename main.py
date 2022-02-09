import logging
import os
import random
import requests
import sys
import telegram
import time

import secret
from config import HOMEWORK_STATUSES, RETRY_TIME, method_upload_const, \
    format_log

file_log = logging.FileHandler(filename='Logfile.log', encoding='UTF-8')
console_out = logging.StreamHandler()

logging.basicConfig(handlers=(file_log, console_out),
                    format=format_log,
                    level=logging.INFO)


def send_message(bot, message, chat_id):
    """Функция отправки сообщения пользователю в Телеграмм."""
    try:
        bot.send_message(
            chat_id=chat_id,
            text=message
        )
        logging.info('Отправлено сообщение: "' + message + '"')
    except telegram.TelegramError as error:
        err = 'Ошибка при отправке сообщения: ' + str(error)
        logging.error(err)


def get_api_answer(url, current_timestamp, token):
    """Функция получения ответа с Практикум.Домашка."""
    current_timestamp = current_timestamp or int(time.time())
    headers = {'Authorization': f'OAuth {token}'}
    payload = {'from_date': current_timestamp}
    response = requests.get(url, headers=headers, params=payload)
    if response.status_code != 200:
        raise requests.RequestException(
            'Ошибка доступа к Практикум.Домашка'
        )
    return response.json()


def parse_status(homework):
    """Функция получения вердикта домашней работы."""
    homework_status = homework.get('status')
    homework_name = homework.get('homework_name')
    lesson_name = homework.get('lesson_name')
    reviewer_comment = homework.get('reviewer_comment')
    if not homework_status or not homework_name:
        raise ValueError('В запросе домашней работы нет необходимых ключей')
    if homework_status not in HOMEWORK_STATUSES:
        raise ValueError('Недокументированный статус работы')
    verdict_answear = random.choice(HOMEWORK_STATUSES[homework_status])
    message = ''
    if lesson_name:
        message += '\nНазвание спринта: ' + lesson_name
    if reviewer_comment:
        message += '\nКомментарий ревьюера: ' + reviewer_comment
    return (f'Изменился статус проверки работы '
            f'"{homework_name}". \n{verdict_answear}'
            f'{message}')


def check_response(response):
    """Функция получения статуса домашней работы."""
    if 'homeworks' not in response:
        raise ValueError('В запросе нет ключа "homeworks"')
    homeworks = response['homeworks']
    if not isinstance(homeworks, list):
        raise TypeError('В запросе под ключом "homeworks" не список')
    if not homeworks:
        return False
    return homeworks[0]


def choise_method_upload_const(method):
    """Функция выбора способа загрузки констант"""
    constants = dict()
    if method.lower() == 'file':
        constants['PRACTICUM_TOKEN'] = secret.PRACTICUM_TOKEN
        constants['CHAT_ID'] = secret.CHAT_ID
        constants['TELEGRAM_TOKEN'] = secret.TELEGRAM_TOKEN
        constants['ENDPOINT'] = secret.ENDPOINT
    else:
        constants['PRACTICUM_TOKEN'] = os.environ.get('PRACTICUM_TOKEN')
        constants['CHAT_ID'] = os.environ.get('CHAT_ID')
        constants['TELEGRAM_TOKEN'] = os.environ.get('TELEGRAM_TOKEN')
        constants['ENDPOINT'] = os.environ.get('ENDPOINT')
    return constants


def checking_constants(constants):
    """Функция проверки загрузки констант."""
    for key, value in constants.items():
        if value is None:
            message = 'Не задана переменная: ' + key
            logging.critical(message)
            return False
    return True


def polling(bot, constants):
    """Функция циклического опроса API и информирования пользователя."""
    current_timestamp = int(time.time())
    last_error = None
    while True:
        try:
            response = get_api_answer(url=constants['ENDPOINT'],
                                      current_timestamp=current_timestamp,
                                      token=constants['PRACTICUM_TOKEN']
                                      )
            current_timestamp = response.get('current_date')
            homework = check_response(response)
            if homework:
                message = parse_status(homework)
                send_message(bot, message, constants['CHAT_ID'])
            else:
                logging.info('В запросе нет изменений по работе')
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            if last_error != message:
                last_error = message
                send_message(bot, message, constants['CHAT_ID'])
            logging.error(error)
            time.sleep(RETRY_TIME / 4)


def main():
    """Функция создания и запуска бота"""
    constants = choise_method_upload_const(method_upload_const)
    if not checking_constants(constants):
        sys.exit()
    try:
        bot = telegram.Bot(token=constants['TELEGRAM_TOKEN'])
    except Exception as error:
        logging.error('Ошибка при создании бота: ' + str(error))
        sys.exit()
    send_message(bot, 'Бот запущен', constants['CHAT_ID'])    
    polling(bot, constants)


if __name__ == '__main__':
    main()
