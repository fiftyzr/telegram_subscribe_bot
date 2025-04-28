import logging
from telethon import TelegramClient, events
import sqlite3

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Ваши данные
api_id = '22011892'  # Замените на ваш API ID
api_hash = '1d2c54a27a6590697dd0668c8e4e6bcd'  # Замените на ваш API Hash

# Создаем клиент с сессией
client = TelegramClient('my_session', api_id, api_hash)

# Канал для подписки
CHANNEL_ID = '@your_channel'  # Замените на ваш канал

# Список разрешенных администраторов по username
admin_usernames = ['fiftyzz']  # Убрали 'fiftyzoro'

# Создание базы данных для хранения подписчиков
conn = sqlite3.connect('subscribers.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS subscribers (user_id INTEGER PRIMARY KEY)''')
conn.commit()

# Стартовое сообщение и кнопки
@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    try:
        user_id = event.sender_id
        # Добавляем пользователя в базу, если его нет
        if user_id not in [row[0] for row in cursor.execute('SELECT user_id FROM subscribers')]:
            cursor.execute('INSERT INTO subscribers (user_id) VALUES (?)', (user_id,))
            conn.commit()

        # Если пользователь администратор, показываем админскую кнопку
        if event.sender.username in admin_usernames:
            # Отправляем сообщение с кнопками для администратора
            await event.respond('Привет, администратор! Вот кнопка для тебя.')
        else:
            await event.respond('Привет! Ты не администратор. Приятного общения!')

    except Exception as e:
        logging.error(f"Ошибка при обработке /start: {e}")

# Функция для подписки на канал
@client.on(events.NewMessage(pattern='Подписаться на канал'))
async def subscribe(event):
    try:
        user_id = event.sender_id
        # Проверка подписки
        try:
            # Проверяем, подписан ли пользователь на канал
            participant = await client.get_participant(CHANNEL_ID, user_id)
            if participant:
                await event.respond('Вы уже подписаны на канал!')
        except:
            await event.respond(f'Для подписки перейдите по [ссылке](https://t.me/+C3aA9_mFLV00NTIy) и нажмите "Присоединиться".', parse_mode='markdown')

    except Exception as e:
        logging.error(f"Ошибка при обработке подписки: {e}")

# Обработка нажатия админской кнопки
@client.on(events.NewMessage(pattern='Админская кнопка'))
async def admin_button(event):
    try:
        if event.sender.username in admin_usernames:
            await event.respond("Ты нажал на админскую кнопку!")
        else:
            await event.respond("Ты не можешь нажимать эту кнопку!")

    except Exception as e:
        logging.error(f"Ошибка при обработке админской кнопки: {e}")

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

# Запуск клиента
async def main():
    try:
        logging.info("Бот запущен...")
        await client.start()
        await client.run_until_disconnected()

    except Exception as e:
        logging.error(f"Ошибка при запуске бота: {e}")

# Запуск асинхронной функции
import asyncio
asyncio.run(main())