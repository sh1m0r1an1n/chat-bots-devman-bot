# Devman Review Bot 🤖

Бот для отслеживания статуса проверки работ на платформе Devman (https://dvmn.org).

## Функционал

- Автоматическое оповещение в Telegram о результатах проверки работ
- Поддержка long-polling API Devman
- Настройка через переменные окружения
- Логирование событий в Telegram

## Требования

- Python 3.8+
- Учетная запись на Devman
- Telegram бот (создается через @BotFather)

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/sh1m0r1an1n/chat-bots-devman-bot
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

## Запуск на сервере

1. Подготовка сервера
- Арендуйте VPS (например, Ubuntu 22.04)
- Получите данные доступа: IP, username (обычно root), пароль
- Подключитесь:
```bash
ssh root@ваш_IP
```

2. Настройка SSH-доступа
- На локальной машине создайте ключи:
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
``` 
- Скопируйте публичный ключ на сервер:
```bash
ssh-copy-id root@ваш_IP
``` 
- На сервере запретите вход по паролю:
```bash
nano /etc/ssh/sshd_config
``` 
Установите:
```text
PasswordAuthentication no
ChallengeResponseAuthentication no
``` 
- Перезапустите SSH:
```bash
systemctl restart sshd
``` 

3. Настройка доступа к GitHub
- Добавьте публичный ключ в GitHub (Settings → SSH and GPG keys)
- Включите SSH Agent Forwarding в `~/.ssh/config`:
```text
Host ваш_сервер
  HostName ваш_IP
  User root
  ForwardAgent yes
``` 

4. Установка бота
- На сервере:
```bash
apt update && apt install -y git python3-venv
git clone git@github.com:sh1m0r1an1n/chat-bots-devman-bot.git
cd chat-bots-devman-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
``` 

4. Настройка systemd
- Создайте сервисный файл:
```bash
nano /etc/systemd/system/devman-bot.service
``` 
- Добавьте конфигурацию:
```ini
[Unit]
Description=Devman Review Bot
After=network.target

[Service]
User=root
WorkingDirectory=/root/chat-bots-devman-bot
ExecStart=/root/chat-bots-devman-bot/venv/bin/python /root/chat-bots-devman-bot/devman-review-bot.py
Restart=always
Environment="PATH=/root/chat-bots-devman-bot/venv/bin"

[Install]
WantedBy=multi-user.target
```
- Запустите бота:
```bash
systemctl daemon-reload
systemctl enable devman-bot
systemctl start devman-bot
``` 

## Проверка работы

```bash
systemctl status devman-bot
journalctl -u devman-bot -f
``` 

## Обновление бота

```bash
cd /root/chat-bots-devman-bot
git pull
systemctl restart devman-bot
``` 