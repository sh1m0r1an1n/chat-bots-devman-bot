import os
import time

from dotenv import load_dotenv
import requests
from telegram import Bot, TelegramError


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

    bot = Bot(token=bot_token)
    bot.send_message(chat_id=chat_id, text=message)


def check_dvmn_reviews(api_token, bot_token, chat_id, timeout = 90, retry_delay = 5):
    """Опрашивает API Devman на наличие новых проверок."""
    headers = {"Authorization": f"Token {api_token}"}
    long_polling_url = "https://dvmn.org/api/long_polling/"
    timestamp = None

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
                for attempt in review_data["new_attempts"]:
                    send_telegram_notification(bot_token, chat_id, attempt)
                timestamp = review_data["last_attempt_timestamp"]
            elif review_data["status"] == "timeout":
                timestamp = review_data["timestamp_to_request"]

        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError:
            time.sleep(retry_delay)
            continue
        except (requests.exceptions.RequestException, TelegramError):
            continue


def main():
    """Основная функция запуска бота."""
    load_dotenv()

    try:
        api_token = os.environ["DVMN_API_TOKEN"]
        bot_token = os.environ["TELEGRAM_BOT_TOKEN"]
        chat_id = os.environ["TELEGRAM_CHAT_ID"]
    except KeyError as e:
        raise ValueError(f"Отсутствует обязательная переменная окружения: {e}")

    check_dvmn_reviews(api_token, bot_token, chat_id)

if __name__ == "__main__":
    main()