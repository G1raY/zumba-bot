import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import glob
import json
import time

from dotenv import load_dotenv

load_dotenv()

bot = telebot.TeleBot(os.environ["BOT_TOKEN"])

adminss = [int(x) for x in os.environ["ADMIN_IDS"].split(",")]
user_states = {}
admin_states = {}
tickets = {}
message_to_delete = {}
admin_messages = {}
active_payments = {}
broadcast_messages = {}
requests = {'help': []}

def get_user_data(user_id, username):
    if not os.path.exists("Users"):
        os.makedirs("Users")
    user_folder = f"Users/{user_id}"
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
        os.makedirs(os.path.join(user_folder, "Purchase"), exist_ok=True)
        os.makedirs(os.path.join(user_folder, "Reservation"), exist_ok=True)
    file_path = f"{user_folder}/{user_id}.json"
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        user_data = {
            "Username": username,
            "Id": user_id,
            "Purchases": 0,
            "Balance": 0
        }
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(user_data, f, ensure_ascii=False, indent=4)
        return user_data

def show_menu(chat_id, message_id=None, user_name="", user_id=None):
    welcome_text = (f'👋Привет, @{user_name}!\n\n'
                    'Вы попали в бота для покупки абонементов на тренировки.\n\n'
                    'В разделе "Купить" можно также взять пробный абонемент.\n\n'
                    'Все управление осуществляется благодаря кнопкам ниже:')
    markup = InlineKeyboardMarkup(row_width=3)
    buttons = [
        InlineKeyboardButton(text='❓О боте', callback_data='info'),
        InlineKeyboardButton(text='💃Zumba?', callback_data='zumba'),
        InlineKeyboardButton(text='📰Канал', url='https://t.me/enkafitness'),
        InlineKeyboardButton(text='💸Купить', callback_data='pay'),
        InlineKeyboardButton(text="📞У меня проблема", callback_data="help")
    ]
    if user_id in adminss:
       buttons.append(InlineKeyboardButton(text='⚙️Панель', callback_data='admin_panel'))
    markup.add(buttons[0], buttons[1], buttons[2])
    markup.add(buttons[3])
    markup.add(buttons[4])
    if len(buttons) > 5:
        markup.add(buttons[5])
    if message_id:
        try:
            bot.edit_message_text(chat_id=chat_id,message_id=message_id,text=welcome_text,reply_markup=markup,parse_mode="HTML",disable_web_page_preview=True)
            return
        except:
            pass
    bot.send_message(chat_id, welcome_text, reply_markup=markup, parse_mode="HTML", disable_web_page_preview=True)

def count_users():
    user_folders = glob.glob("Users/*")
    return len(user_folders)

@bot.message_handler(commands=['start'])
def message_handler(message):
    user_name = message.from_user.username
    user_id = message.from_user.id
    get_user_data(user_id, user_name)
    if user_id in user_states:
        del user_states[user_id]
    show_menu(message.chat.id, user_name=user_name, user_id=user_id)

@bot.callback_query_handler(func=lambda call: call.data == "back_to_menu")
def handle_back_to_menu(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    if user_id in message_to_delete:
        try:
            bot.delete_message(chat_id, message_to_delete[user_id])
            del message_to_delete[user_id]
        except:
            pass
    show_menu(chat_id, message_id, user_name=call.from_user.username, user_id=user_id)

@bot.callback_query_handler(func=lambda call: call.data == "info")
def callback_handler(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    if call.data == 'info':
        info_text = (f'🤔Данный бот предназначен для упрощения жизни тренеру.\n\n'
                         'Вместо постоянного общения с клиентами насчет оплаты, все можно сделать просто в боте\n\n'
                         'Это очень сильно экономит ресурс самого человека и его время.🆙\n\n'
                         'Надеюсь, теперь вам стало чуть-чуть понятней.\n\n'
                         '<b><i>Чтоб вернуться в главное меню, нажмите кнопку Назад</i></b>')
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton(text='◀️Назад', callback_data='back_to_menu'))
    bot.edit_message_text(chat_id=chat_id, message_id=message_id,  text=info_text, reply_markup=markup, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data == 'zumba')
def callback_handler(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    if call.data == 'zumba':
        zumba_text = (f'➡️Зумба — это танцевальная фитнес-программа, сочетающая\n'
                      'элементы латиноамериканских танцев (самбы, сальсы, меренге\n'
                      'и др.) с аэробными упражнениями. Она направлена на\n'
                      'улучшение физической формы, повышение выносливости и\n'
                      'поддержание хорошего настроения благодаря энергичной\n'
                      'музыке и веселым движениям. Подходит людям любого\n'
                      'возраста и уровня подготовки.⬅️\n\n'
                      '<b><i>Чтоб вернуться в главное меню, нажмите кнопку Назад</i></b>')
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton(text='◀️Назад', callback_data='back_to_menu'))
    bot.edit_message_text(chat_id=chat_id, message_id=message_id,  text=zumba_text, reply_markup=markup, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data == "admin_panel")
def handle_admin_panel(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    admin_text = f"Здравствуйте, админ: @{call.from_user.username}. Выберите функцию для использования:"
    markup = InlineKeyboardMarkup(row_width=3)
    button = [
        InlineKeyboardButton(text='📩Рассылка', callback_data='broadcast'),
        InlineKeyboardButton(text='◀️Назад', callback_data='back_to_menu'),
        InlineKeyboardButton(text='📧Запросы', callback_data='view_requests')
    ]
    markup.add(button[0], button[2])
    markup.add(button[1])
    try:
        bot.edit_message_text(chat_id=chat_id,message_id=message_id,text=admin_text,reply_markup=markup)
        broadcast_messages[user_id] = {"admin_panel_id": message_id}
    except Exception as e:
        print(f"Ошибка админ-панели: {e}")

@bot.callback_query_handler(func=lambda call: call.data == "broadcast")
def handle_broadcast(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    broadcast_text = "Введите сообщение для рассылки:"
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("◀️ Назад", callback_data="back_to_admin_panel"))
    try:
        bot.edit_message_text(chat_id=chat_id,message_id=message_id,text=broadcast_text,reply_markup=markup)
        broadcast_messages[user_id]["broadcast_request_id"] = message_id
        user_states[user_id] = {"state": "waiting_broadcast"}
    except Exception as e:
        print(f"Ошибка запроса рассылки: {e}")

@bot.callback_query_handler(func=lambda call: call.data == "back_to_admin_panel")
def handle_back_to_admin_panel(call):
    user_id = call.from_user.id
    handle_admin_panel(call)
    if user_id in user_states and user_states[user_id].get("state") == "waiting_broadcast":
        del user_states[user_id]

@bot.message_handler(content_types=['text', 'photo', 'video'], func=lambda message: (  
    message.from_user.id in user_states and
    isinstance(user_states[message.from_user.id], dict) and
    user_states[message.from_user.id].get("state") == "waiting_broadcast"
))
def handle_broadcast_message(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    if user_id in broadcast_messages and "broadcast_request_id" in broadcast_messages[user_id]:
        try:
            bot.delete_message(chat_id, broadcast_messages[user_id]["broadcast_request_id"])
        except:
            pass
    total_users = count_users()
    success = 0
    failed = 0
    user_folders = glob.glob("Users/*")
    for user_folder in user_folders:
        try:
            user_id_to_send = int(os.path.basename(user_folder))
            if message.photo:
                bot.send_photo(
                    user_id_to_send,
                    message.photo[-1].file_id,
                    caption=message.caption if message.caption else ""
                )
            elif message.video:
                bot.send_video(
                    user_id_to_send,
                    message.video.file_id,
                    caption=message.caption if message.caption else ""
                )
            else:
                bot.send_message(user_id_to_send, message.text)
                
            success += 1
        except Exception as e:
            print(f"Ошибка при рассылке: {e}")
            failed += 1
    report = (
        f"👥 Пользователей: {total_users}\n"
        f"✅ Удалось отправить: {success}\n"
        f"❌ Не удалось отправить: {failed}"
    )
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🏠 Домой", callback_data="back_to_menu"))
    bot.send_message(chat_id, report, reply_markup=markup)

    del user_states[user_id]
    if user_id in broadcast_messages:
        del broadcast_messages[user_id]

@bot.callback_query_handler(func=lambda call: call.data == "help")
def callback_handler(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    if call.data in ["help"]:
        if user_id in message_to_delete:
            try:
                bot.delete_message(chat_id, message_to_delete[user_id])
                del message_to_delete[user_id]
            except:
                pass
        help_text = "🧑‍💻 | Можете отправить сюда свою заявку. Мы ответим вам, как только появится возможность."
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("◀️ Назад", callback_data="back_to_menu"))
        try:
            bot.delete_message(chat_id, message_id)
        except:
            pass
        bot.send_message(chat_id, help_text, reply_markup=markup)
        user_states[user_id] = {"state": "waiting_for_request", "category": call.data}

@bot.message_handler(content_types=['text', 'photo', 'video'])
def handle_messages(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    user_name = message.from_user.username
    if user_id in user_states and user_states[user_id].get("state") == "waiting_for_request":
        if user_id in message_to_delete:
            try:
                bot.delete_message(chat_id, message_to_delete[user_id])
                del message_to_delete[user_id]
            except:
                pass
        category = user_states[user_id]["category"]
        problem_text = message.caption if message.caption else message.text
        has_photo = False
        photo_id = None
        has_video = False
        video_id = None
        if message.photo:
            has_photo = True
            photo_id = message.photo[-1].file_id
        elif message.video:
                has_video = True
                video_id = message.video.file_id
        if not problem_text:
            problem_text = "None"
        confirm_text = "<b>✉️ Ваша заявка успешно создана.</b>\nПожалуйста, ожидайте ответа от администрации. Обычно время ответа составляет до 1 часа, но в случае высокой загруженности оно может увеличиться до 24 часов!"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("◀️ Назад", callback_data="back_to_menu"))
        try:
            bot.delete_message(chat_id, message.message_id)
        except:
            pass
        confirm_msg = bot.send_message(chat_id, confirm_text, parse_mode="HTML", reply_markup=markup)
        message_to_delete[user_id] = confirm_msg.message_id
        request_data = {
            "user_id": user_id,
            "username": user_name,
            "text": problem_text,
            "video_id": video_id if has_video else None,
            "photo_id": photo_id if has_photo else None,
            "timestamp": time.time(),
            "category": category
        }
        requests[category].append(request_data)
        for admin_id in adminss:
            try:
                bot.send_message(admin_id, "📨 [+1] Запрос в поддержку!")
            except Exception as e:
                print(f"Ошибка отправки уведомления админу {admin_id}: {e}")
        del user_states[user_id]

@bot.callback_query_handler(func=lambda call: call.data == "pay")
def callback_handler(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    pay_text = (f'<i>Выберите подходящую вам категорию:</i>')
    markup = InlineKeyboardMarkup(row_width= 2)
    buttons = [
        InlineKeyboardButton(text='🕑Пробный', callback_data='trial'),
        InlineKeyboardButton(text='📆Обычный', callback_data='defolt'),
        InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")
    ]
    markup.add(*buttons)
    bot.edit_message_text(chat_id=chat_id,message_id=message_id,text=pay_text,reply_markup=markup, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    if call.data == "view_requests":
        markup = InlineKeyboardMarkup(row_width=1)
        buttons = [
            InlineKeyboardButton("🆘 Помощь", callback_data="list_requests:help"),
            InlineKeyboardButton("◀️ Назад", callback_data="back_to_menu")
        ]
        markup.add(*buttons)
        try:
            bot.delete_message(chat_id, message_id)
        except:
            pass
        bot.send_message(chat_id, "Выберите категорию для просмотра заявок:", reply_markup=markup)
    elif call.data.startswith("list_requests:"):
        category = call.data.split(":")[1]
        req_list = requests[category]
        try:
            bot.delete_message(chat_id, message_id)
        except:
            pass
        if not req_list:
            text = "Заявок в этой категории пока нет."
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("◀️ Назад", callback_data="view_requests"))
            bot.send_message(chat_id, text, reply_markup=markup)
        else:
            markup = InlineKeyboardMarkup()
            for index, req in enumerate(req_list):
                time_str = time.strftime("%H:%M | %d %B", time.localtime(req['timestamp']))
                button_text = f"@{req['username']} - {time_str}"
                callback_data = f"view_request:{category}:{index}"
                markup.add(InlineKeyboardButton(button_text, callback_data=callback_data))
            markup.add(InlineKeyboardButton("◀️ Назад", callback_data="view_requests"))
            bot.send_message(chat_id, "Выберите заявку для просмотра:", reply_markup=markup)
    elif call.data.startswith("view_request:"):
        parts = call.data.split(":")
        category = parts[1]
        index = int(parts[2])
        req = requests[category][index]
        text = f"👤 Пользователь: @{req['username']}\n🆔 ID: {req['user_id']}\n📝 Сообщение пользователя: {req['text']}"
        markup = InlineKeyboardMarkup(row_width=2)
        reply_btn = InlineKeyboardButton("💬 Ответить", callback_data=f"reply_request:{category}:{index}")
        delete_btn = InlineKeyboardButton("🗑️ Удалить", callback_data=f"delete_request:{category}:{index}")
        back_btn = InlineKeyboardButton("◀️ Назад", callback_data=f"list_requests:{category}")
        markup.add(reply_btn, delete_btn, back_btn)
        try:
            bot.delete_message(chat_id, message_id)
        except:
            pass
        
        if req.get('photo_id'):
            bot.send_photo(chat_id, req['photo_id'], caption=text, reply_markup=markup)
        else:
            bot.send_message(chat_id, text, reply_markup=markup)
    elif call.data.startswith("delete_request:"):
        parts = call.data.split(":")
        category = parts[1]
        index = int(parts[2])
        del requests[category][index]
        try:
            bot.delete_message(chat_id, message_id)
        except:
            pass
        req_list = requests[category]
        if not req_list:
            text = "Заявок в этой категории пока нет."
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("◀️ Назад", callback_data="view_requests"))
            bot.send_message(chat_id, text, reply_markup=markup)
        else:
            markup = InlineKeyboardMarkup()
            for idx, req in enumerate(req_list):
                time_str = time.strftime("%H:%M | %d %B", time.localtime(req['timestamp']))
                button_text = f"@{req['username']} - {time_str}"
                callback_data = f"view_request:{category}:{idx}"
                markup.add(InlineKeyboardButton(button_text, callback_data=callback_data))
            markup.add(InlineKeyboardButton("◀️ Назад", callback_data="view_requests"))
            bot.send_message(chat_id, "Выберите заявку для просмотра:", reply_markup=markup)
    elif call.data.startswith("reply_request:"):
        parts = call.data.split(":")
        category = parts[1]
        index = int(parts[2])
        req = requests[category][index]
        admin_states[user_id] = {
            "state": "replying",
            "category": category,
            "index": index,
            "request": req,
            "original_message_id": message_id
        }
        text = "Введите ответ для пользователя:"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("◀️ Назад", callback_data=f"view_request:{category}:{index}"))
        try:
            bot.delete_message(chat_id, message_id)
        except:
            pass
        bot.send_message(chat_id, text, reply_markup=markup)


if __name__ == "__main__":
    print("Бот начал свою работу...")
    bot.infinity_polling(timeout=60, long_polling_timeout=30)
        