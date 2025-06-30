# Devman Review Bot 🤖

Бот для отслеживания статуса проверки работ на платформе Devman (https://dvmn.org).

## Функционал

- Автоматическое оповещение в Telegram о результатах проверки работ
- Поддержка long-polling API Devman
- Настройка через переменные окружения

## Требования

- Python 3.8+
- Учетная запись на Devman
- Telegram бот (создается через @BotFather)

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/devman-review-bot.git
cd devman-review-bot
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте файл `.env` и заполните его:
```ini
DVMN_API_TOKEN=ваш_токен_devman
TELEGRAM_BOT_TOKEN=токен_вашего_бота
TELEGRAM_CHAT_ID=ваш_chat_id
```

## Запуск
```bash
python devman-review-bot.py
```
