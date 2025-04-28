import logging
import sqlite3
import asyncio
from telethon import TelegramClient, events, functions

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Ваши данные
api_id = 22011892  # Без кавычек, число
api_hash = '1d2c54a27a6590697dd0668c8e4e6bcd'
bot_token = '7879222970:AAExi2jRBLlCl5TgcDWXmZK_OpBmRs0Dllw'

# Создаем клиент с сессией через токен бота
client = TelegramClient('bot_session', api_id, api_hash).start(bot_token=bot_token)

# Канал для подписки
CHANNEL_ID = '@your_channel'  # <-- замени на свой канал обязательно!

# Список разрешенных администраторов
admin_usernames = ['fiftyzz']

# Создание базы данных для хранения подписчиков
conn = sqlite3.connect('subscribers.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS subscribers (user_id INTEGER PRIMARY KEY)''')
conn.commit()

# Обработчик всех новых сообщений
@client.on(events.NewMessage)
async def handler(event):
    text = event.raw_text.strip()

    # Команда старт
    if text == "/start":
        try:
            user_id = event.sender_id
            # Добавляем пользователя в базу, если его нет
            if user_id not in [row[0] for row in cursor.execute('SELECT user_id FROM subscribers')]:
                cursor.execute('INSERT INTO subscribers (user_id) VALUES (?)', (user_id,))
                conn.commit()

            if event.sender.username in admin_usernames:
                await event.respond('Привет, администратор! Вот кнопка для тебя.')
            else:
                await event.respond('Привет! Ты не администратор. Приятного общения!')

        except Exception as e:
            logging.error(f"Ошибка в /start: {e}")

    # Кнопка подписки
    elif text == "Подписаться на канал":
        try:
            user_id = event.sender_id
            try:
                participant = await client(functions.channels.GetParticipantRequest(
                    channel=CHANNEL_ID,
                    participant=user_id
                ))
                if participant:
                    await event.respond('Вы уже подписаны на канал!')
            except:
                await event.respond(
                    'Для подписки перейдите по [ссылке](https://t.me/+C3aA9_mFLV00NTIy) и нажмите "Присоединиться".',
                    parse_mode='markdown'
                )
        except Exception as e:
            logging.error(f"Ошибка при подписке: {e}")

    # Админская кнопка
    elif text == "Админская кнопка":
        try:
            if event.sender.username in admin_usernames:
                await event.respond("Ты нажал на админскую кнопку!")
            else:
                await event.respond("Ты не можешь нажимать эту кнопку!")
        except Exception as e:
            logging.error(f"Ошибка в админской кнопке: {e}")

# Функция для рассылки сообщения всем подписчикам
async def send_message_to_all_subscribers(message_text):
    try:
        for subscriber in cursor.execute('SELECT user_id FROM subscribers'):
            try:
                await client.send_message(subscriber[0], message_text)
            except Exception as e:
                logging.error(f"Не удалось отправить сообщение пользователю {subscriber[0]}: {e}")
    except Exception as e:
        logging.error(f"Ошибка при рассылке сообщения: {e}")

# Основная функция запуска
async def main():
    try:
        logging.info("Бот запущен...")
        await client.run_until_disconnected()
    except Exception as e:
        logging.error(f"Ошибка при запуске бота: {e}")

# Запуск
asyncio.run(main())
