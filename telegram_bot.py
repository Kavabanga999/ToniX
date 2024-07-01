import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import requests

TOKEN = '7452719949:AAGQpWGUTYftlbxTTzEvul38OBKVX6NtHSI'
API_URL = 'https://7d74-46-211-122-112.ngrok-free.app'  # Обновите URL на ваш Glitch URL

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton("🔥 Start App 🔥", web_app=WebAppInfo(url=API_URL))
        ],
        [
            InlineKeyboardButton("📖 Read me 📖", callback_data='info'),
            InlineKeyboardButton("📣 News 📣", callback_data='news'),
            InlineKeyboardButton("💬 Chat 💬", callback_data='chat')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    description = """
Добро пожаловать в ТОНИКС!

🚀 Откройте для себя революционное приложение Mine-To-Earn, созданное на платформе Telegram!

Испытайте безграничные возможности облачного майнинга биткойнов. Наша инфраструктура, основанная на блокчейне TON, обеспечивает оптимизацию транзакций и снижение комиссий за перевод.

Будьте среди пионеров заработка с Tonix!

Выполняйте миссии, приглашайте друзей, арендуйте дополнительные мощности для майнинга, чтобы зарабатывать еще больше. 

Не упустите возможность увеличить свой доход и стремиться к финансовой независимости вместе с нами! ⚡️💰🚀

Нажмите «Запустить приложение» 👇.
"""

    # Send the photo first
    photo_path = 'path/to/your/photo.jpg'  # Обновите путь к фото
    try:
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(photo_path, 'rb'))
    except Exception as e:
        logging.error(f"Error sending photo: {e}")

    # Then send the description with the buttons
    await update.message.reply_text(description, reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'info':
        await query.edit_message_text(text="Информация о майнинге: ...")
    elif query.data == 'news':
        await query.edit_message_text(text="Последние новости: ...")
    elif query.data == 'chat':
        await query.edit_message_text(text="Чат: ...")

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    wallet_address = "USER_WALLET_ADDRESS"  # замените на реальный способ получения адреса кошелька
    try:
        response = requests.post(f'{API_URL}/api/register', json={"username": user.username, "wallet_address": wallet_address})
        if response.status_code == 201:
            await update.message.reply_text(f"Регистрация успешна! {response.json()}")
        else:
            await update.message.reply_text(f"Ошибка регистрации: {response.json()['message']}")
    except Exception as e:
        logging.error(f"Error registering user: {e}")
        await update.message.reply_text(f"Ошибка регистрации: {e}")

async def deposit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    wallet_address = "USER_WALLET_ADDRESS"  # замените на реальный способ получения адреса кошелька
    amount = 10  # замените на реальный способ получения суммы депозита
    try:
        response = requests.post(f'{API_URL}/api/deposit', json={"wallet_address": wallet_address, "amount": amount})
        if response.status_code == 200:
            await update.message.reply_text(f"Депозит успешен! {response.json()}")
        else:
            await update.message.reply_text(f"Ошибка депозита: {response.json()['message']}")
    except Exception as e:
        logging.error(f"Error in deposit: {e}")
        await update.message.reply_text(f"Ошибка депозита: {e}")

async def start_mining(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    wallet_address = "USER_WALLET_ADDRESS"  # замените на реальный способ получения адреса кошелька
    try:
        response = requests.post(f'{API_URL}/api/start_mining', json={"wallet_address": wallet_address})
        if response.status_code == 200:
            await update.message.reply_text(f"Майнинг начат! {response.json()}")
        else:
            await update.message.reply_text(f"Ошибка: {response.json()['message']}")
    except Exception as e:
        logging.error(f"Error starting mining: {e}")
        await update.message.reply_text(f"Ошибка: {e}")

async def stop_mining(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    wallet_address = "USER_WALLET_ADDRESS"  # замените на реальный способ получения адреса кошелька
    try:
        response = requests.post(f'{API_URL}/api/stop_mining', json={"wallet_address": wallet_address})
        if response.status_code == 200:
            await update.message.reply_text(f"Майнинг остановлен! {response.json()}")
        else:
            await update.message.reply_text(f"Ошибка: {response.json()['message']}")
    except Exception as e:
        logging.error(f"Error stopping mining: {e}")
        await update.message.reply_text(f"Ошибка: {e}")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    wallet_address = "USER_WALLET_ADDRESS"  # замените на реальный способ получения адреса кошелька
    try:
        response = requests.get(f'{API_URL}/api/status', params={"wallet_address": wallet_address})
        if response.status_code == 200:
            data = response.json()
            await update.message.reply_text(f"Пользователь: {data['username']}\nБаланс: {data['balance']}\nСкорость майнинга: {data['mining_speed']}\nМайнинг активен: {data['is_mining']}")
        else:
            await update.message.reply_text(f"Ошибка: {response.json()['message']}")
    except Exception as e:
        logging.error(f"Error fetching status: {e}")
        await update.message.reply_text(f"Ошибка: {e}")

def main() -> None:
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CommandHandler('register', register))
    application.add_handler(CommandHandler('deposit', deposit))
    application.add_handler(CommandHandler('start_mining', start_mining))
    application.add_handler(CommandHandler('stop_mining', stop_mining))
    application.add_handler(CommandHandler('status', status))
    
    application.run_polling()

if __name__ == '__main__':
    main()
