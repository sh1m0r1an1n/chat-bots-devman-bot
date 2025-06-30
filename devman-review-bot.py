import os
from dotenv import load_dotenv

import requests
from telegram import Bot, TelegramError


load_dotenv()

DVMN_API_TOKEN = os.getenv("DVMN_API_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
LONG_POLLING_URL = "https://dvmn.org/api/long_polling/"
REQUEST_TIMEOUT = 90


def send_telegram_notification(attempt: dict) -> None:
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

    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)


def check_dvmn_reviews() -> None:
    """Опрашивает API Devman на наличие новых проверок."""
    if not all([DVMN_API_TOKEN, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID]):
        raise ValueError("Не найдены необходимые переменные окружения")

    headers = {"Authorization": f"Token {DVMN_API_TOKEN}"}
    timestamp = None

    while True:
        try:
            params = {"timestamp": timestamp} if timestamp else {}
            response = requests.get(
                url=LONG_POLLING_URL,
                headers=headers,
                params=params,
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()

            review_data = response.json()

            if review_data["status"] == "found":
                for attempt in review_data["new_attempts"]:
                    send_telegram_notification(attempt)
                timestamp = review_data["last_attempt_timestamp"]
            elif review_data["status"] == "timeout":
                timestamp = review_data["timestamp_to_request"]

        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError:
            continue
        except (requests.exceptions.RequestException, TelegramError):
            continue


if __name__ == "__main__":
    check_dvmn_reviews()