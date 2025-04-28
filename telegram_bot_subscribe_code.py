import logging
import sqlite3
import asyncio
import os
from telethon import TelegramClient, events

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Ваши данные (берем из переменных окружения или напрямую вписываем)
api_id = 22011892  # Ваш api_id
api_hash = '1d2c54a27a6590697dd0668c8e4e6bcd'  # Ваш api_hash
bot_token = '7879222970:AAExi2jRBLlCl5TgcDWXmZK_OpBmRs0Dllw'  # Ваш токен бота

# Создаем клиент и сразу передаем токен
client = TelegramClient('my_session', api_id, api_hash).start(bot_token=bot_token)

# Канал для подписки
CHANNEL_ID = '@your_channel'  # Замените на ваш канал

# Список разрешенных администраторов по username
admin_usernames = ['fiftyzz']

# Создание базы данных для хранения подписчиков
conn = sqlite3.connect('subscribers.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS subscribers (
    user_id INTEGER PRIMARY KEY
)
''')
conn.commit()

# Стартовое сообщение
@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    try:
        user_id = event.sender_id
        # Добавляем пользователя в базу, если его нет
        cursor.execute('SELECT 1 FROM subscribers WHERE user_id = ?', (user_id,))
        if cursor.fetchone() is None:
            cursor.execute('INSERT INTO subscribers (user_id) VALUES (?)', (user_id,))
            conn.commit()

        # Проверяем админа
        if event.sender.username in admin_usernames:
            await event.respond('Привет, администратор! Вот кнопка для тебя.')
        else:
            await event.respond('Привет! Ты не администратор. Приятного общения!')

    except Exception as e:
        logging.error(f"Ошибка при обработке команды /start: {e}")

# Подписка на канал
@client.on(events.NewMessage(pattern='Подписаться на канал'))
async def subscribe(event):
    try:
        user_id = event.sender_id
        try:
            participant = await client.get_participant(CHANNEL_ID, user_id)
            if participant:
                await event.respond('Вы уже подписаны на канал!')
        except:
            await event.respond(
                'Для подписки перейдите по [ссылке](https://t.me/+C3aA9_mFLV00NTIy) и нажмите "Присоединиться".',
                parse_mode='markdown'
            )
    except Exception as e:
        logging.error(f"Ошибка при проверке подписки: {e}")

# Кнопка администратора
@client.on(events.NewMessage(pattern='Админская кнопка'))
async def admin_button(event):
    try:
        if event.sender.username in admin_usernames:
            await event.respond('Ты нажал на админскую кнопку!')
        else:
            await event.respond('Ты не можешь нажимать эту кнопку!')
    except Exception as e:
        logging.error(f"Ошибка при обработке админской кнопки: {e}")

# Рассылка сообщения всем подписчикам
async def send_message_to_all_subscribers(message_text):
    try:
        for (user_id,) in cursor.execute('SELECT user_id FROM subscribers'):
            try:
                await client.send_message(user_id, message_text)
            except Exception as e:
                logging.error(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
    except Exception as e:
        logging.error(f"Ошибка при рассылке сообщения: {e}")

# Основная функция
async def main():
    logging.info("Бот запущен...")
    await client.run_until_disconnected()

# Старт
if __name__ == '__main__':
    asyncio.run(main())
