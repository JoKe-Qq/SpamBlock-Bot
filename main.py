from flask import Flask, request
import telebot
import os

TOKEN = os.getenv('TOKEN')
OWNER_ID = 855863746

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Кэш для хранения юзернеймов и ID
user_cache = {}

@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    print(json_str)  # Лог запроса от Telegram для отладки
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return 'OK', 200

# Пересылка всех сообщений владельцу
@bot.message_handler(func=lambda message: message.chat.id != OWNER_ID and not message.text.startswith('/reply'))
def forward_to_owner(message):
    if message.from_user.username:
        user_cache[message.from_user.username] = message.chat.id
    else:
        user_cache[str(message.from_user.id)] = message.chat.id

    user_info = f"👤 @{message.from_user.username}" if message.from_user.username else f"👤 ID: {message.from_user.id}"
    bot.send_message(OWNER_ID, f"{user_info}\n\n{message.text}")

# Обработка команды /reply (только от владельца)
@bot.message_handler(commands=['reply'])
def reply_to_user(message):
    if message.chat.id != OWNER_ID:
        return

    try:
        args = message.text.split(maxsplit=2)
        if len(args) < 3:
            bot.send_message(OWNER_ID, "❗️ Используй так: /reply <user_id или @юзернейм> <текст>")
            return

        target = args[1]
        text_to_send = args[2]

        if target.startswith('@'):
            target_username = target[1:]
            if target_username in user_cache:
                user_id = user_cache[target_username]
            else:
                bot.send_message(OWNER_ID, "❗️ Бот ещё не видел этого пользователя")
                return
        else:
            user_id = int(target)

        bot.send_message(user_id, text_to_send)
        bot.send_message(OWNER_ID, "✅ Сообщение отправлено!")

    except ValueError:
        bot.send_message(OWNER_ID, "❗️ Неправильный формат ID или юзернейма")

@app.route('/')
def home():
    return "Бот работает!"

if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url='https://web-production-05d5.up.railway.app/' + TOKEN)
    app.run(host='0.0.0.0', port=5000)
