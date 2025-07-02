import logging
import os
import time
import traceback

from dotenv import load_dotenv
import requests
from telegram import Bot, TelegramError


class TelegramLogHandler(logging.Handler):
    """Отправляет логи в Telegram"""

    def __init__(self, bot_token, chat_id, level=logging.INFO):
        super().__init__(level=level)
        self.bot = Bot(token=bot_token)
        self.chat_id = chat_id

    def emit(self, record):
        """Отправка сообщения с логом"""
        log_entry = self.format(record)
        self.bot.send_message(chat_id=self.chat_id, text=log_entry)


def setup_logging(bot_token, chat_id):
    """Настройка логирования для Telegram"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    logger.handlers.clear()

    telegram_handler = TelegramLogHandler(bot_token, chat_id)
    telegram_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    )
    logger.addHandler(telegram_handler)


def send_telegram_notification(bot_token, chat_id, attempt):
    """Отправляет уведомление в Telegram о новой проверке."""
    lesson_title = attempt["lesson_title"]
    status = "❌ Есть замечания" if attempt["is_negative"] else "✅ Принято"
    lesson_url = attempt.get("lesson_url", "")

    message = (
        f"Новая проверка!\n"
        f"Урок: {lesson_title}\n"
        f"Статус: {status}\n"
        f"Ссылка: {lesson_url}"
    )

    try:
        bot = Bot(token=bot_token)
        bot.send_message(chat_id=chat_id, text=message)
    except TelegramError as e:
        logging.error(f"Failed to send Telegram notification: {e}")


def check_dvmn_reviews(api_token, bot_token, chat_id, timeout = 90, retry_delay = 5):
    """Опрашивает API Devman на наличие новых проверок."""
    headers = {"Authorization": f"Token {api_token}"}
    long_polling_url = "https://dvmn.org/api/long_polling/"
    timestamp = None

    logging.info("Бот запущен и начал проверку работ")

    while True:
        try:
            params = {"timestamp": timestamp} if timestamp else {}
            response = requests.get(
                url=long_polling_url,
                headers=headers,
                params=params,
                timeout=timeout
            )
            response.raise_for_status()

            review_data = response.json()

            if review_data["status"] == "found":
                logging.info(f"Найдены новые проверки: {len(review_data['new_attempts'])}")
                for attempt in review_data["new_attempts"]:
                    send_telegram_notification(bot_token, chat_id, attempt)
                timestamp = review_data["last_attempt_timestamp"]
            elif review_data["status"] == "timeout":
                timestamp = review_data["timestamp_to_request"]

        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError:
            logging.warning("Ошибка соединения, повторная попытка...")
            time.sleep(retry_delay)
            continue
        except (requests.exceptions.RequestException, TelegramError) as e:
            logging.exception(f"Ошибка запроса: {e}")
            time.sleep(retry_delay)
            continue


def main():
    """Основная функция запуска бота."""
    load_dotenv()

    try:
        api_token = os.environ["DVMN_API_TOKEN"]
        bot_token = os.environ["TELEGRAM_BOT_TOKEN"]
        chat_id = os.environ["TELEGRAM_CHAT_ID"]
    except KeyError as e:
        logging.exception(f"Отсутствует переменная окружения: {e}")
        raise

    setup_logging(bot_token, chat_id)
    check_dvmn_reviews(api_token, bot_token, chat_id)

if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            logging.critical(f"Критическая ошибка: {e}\n{traceback.format_exc()}")
            time.sleep(5)