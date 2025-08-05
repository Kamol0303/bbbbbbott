import telebot
from telebot import types
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
import os

# .env faylini yuklash
load_dotenv()

# Sozlamalar
API_TOKEN = os.getenv("API_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
bot = telebot.TeleBot(API_TOKEN)

# Foydalanuvchi holatlari
user_state = {}
user_language = {}  # {chat_id: 'uz' yoki 'ru'}

# Tillar lug'ati
translations = {
    'uz': {     
        'welcome': "👋 Assalamu alaykum, 21-asr kompyuter xizmatlari.Ro'yxatdan o'ting, sizga xizmatlarimizni ro'yxatini beramiz!",
        'register': "📋 Ro'yxatdan o'tish",
        'contact': "📞 Bog'lanish",
        'send_file': "📥 Murojaat yuborish",
        'back': "🔙 Orqaga qaytish",
        'change_lang': "🌐 Tilni o'zgartirish",
        'admin_welcome': "👨‍💻 Admin paneliga xush kelibsiz!",
        'no_access': "⚠️ Sizga ruxsat yo'q!",
        'stats': "📊 Statistika",
        'broadcast': "📢 Xabar yuborish",
        'main_menu': "🏠 Bosh menyu",
        'enter_name': "Iltimos, ismingizni kiriting:",
        'phone_request': "📱Telefon raqamngizni kiriting yoki kontakt yuborish tugmasini bosing:",
        'phone_button': "📞 Kontakt yuborish",
        'invalid_phone': "⚠️ Noto'g'ri format. Iltimos, +998901234567 formatida kiriting yoki kontakt yuboring.",
        'registered': "✅ Ro'yxatdan o'tdingiz!\nIsm: {}\nTel: {}",
        'new_user': "⚠️ Yangi foydalanuvchi:\n👤 {}\n📞 {}\n🆔 {}"
    },
    'ru': {
        'welcome': "👋 Здравствуйте, 21-й век компьютерные услуги. После того как вы поделитесь контактом, мы предоставим вам список наших услуг! ",
        'register': "📋 Регистрация",
        'contact': "📞 Контакты",
        'send_file': "📥 Отправить запрос",
        'back': "🔙 Назад",
        'change_lang': "🌐 Изменить язык",
        'admin_welcome': "👨‍💻 Добро пожаловать в админ-панель!",
        'no_access': "⚠️ У вас нет доступа!",
        'stats': "📊 Статистика",
        'broadcast': "📢 Отправить сообщение",
        'main_menu': "🏠 Главное меню",
        'enter_name': "Пожалуйста, введите ваше имя:",
        'phone_request': "📱 Введите свой номер телефона или нажмите кнопку отправки контакта:",
        'phone_button': "📞 Отправить контакт",
        'invalid_phone': "⚠️ Неверный формат. Введите в формате +998901234567 или отправьте контакт.",
        'registered': "✅ Вы зарегистрированы!\nИмя: {}\nТел: {}",
        'new_user': "⚠️ Новый пользователь:\n👤 {}\n📞 {}\n🆔 {}"
    }
}

# Ma'lumotlar bazasini yaratish
def init_db():
    conn = sqlite3.connect('office_bot.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        first_name TEXT,
        phone TEXT,
        registered_at TEXT
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        message_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        message_type TEXT,
        content TEXT,
        file_id TEXT,
        sent_at TEXT
    )
    ''')
    conn.commit()
    conn.close()

init_db()

# Yordamchi funksiyalar
def get_lang(chat_id):
    return user_language.get(chat_id, 'uz')

def back_button(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(translations[get_lang(chat_id)]['back'])
    return markup

def language_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🇺🇿 O'zbekcha", "🇷🇺 Русский")
    return markup

def main_menu(chat_id):
    lang = get_lang(chat_id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    # Tugmalar tartibi: Ro'yxat, Murojaat, Bog'lanish, Til
    buttons = [
        translations[lang]['register'],
        translations[lang]['send_file'],
        translations[lang]['contact'],
        translations[lang]['change_lang']
    ]
    # Qatorlarga joylash
    markup.add(*buttons[0:2])        # Birinchi qator
    markup.add(*buttons[2:])         # Ikkinchi qator
    return markup

def admin_menu(chat_id):
    lang = get_lang(chat_id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        translations[lang]['stats'],
        translations[lang]['broadcast'],
        translations[lang]['main_menu']
    ]
    markup.add(*buttons)
    return markup

# Start handler
@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id == ADMIN_ID:
        lang = get_lang(message.chat.id)
        bot.send_message(message.chat.id, translations[lang]['admin_welcome'], reply_markup=admin_menu(message.chat.id))
    else:
        if message.chat.id not in user_language:
            msg = bot.send_message(message.chat.id, "Iltimos, tilni tanlang:", reply_markup=language_keyboard())
            bot.register_next_step_handler(msg, set_language)
        else:
            lang = get_lang(message.chat.id)
            bot.send_message(message.chat.id, translations[lang]['welcome'], reply_markup=main_menu(message.chat.id))

def set_language(message):
    chat_id = message.chat.id
    if message.text == "🇺🇿 O'zbekcha":
        user_language[chat_id] = 'uz'
    elif message.text == "🇷🇺 Русский":
        user_language[chat_id] = 'ru'
    else:
        msg = bot.send_message(chat_id, "Noto'g'ri tanlov! Iltimos, tilni tanlang:", reply_markup=language_keyboard())
        bot.register_next_step_handler(msg, set_language)
        return
    start(message)

# Tilni o'zgartirish
@bot.message_handler(func=lambda m: m.text in ["🌐 Tilni o'zgartirish", "🌐 Изменить язык"])
def change_language(message):
    msg = bot.send_message(message.chat.id, "Iltimos, tilni tanlang:", reply_markup=language_keyboard())
    bot.register_next_step_handler(msg, set_language)

# Ro'yxatdan o'tish
@bot.message_handler(func=lambda m: m.text in ["📋 Ro'yxatdan o'tish", "📋 Регистрация"])
def register_user(message):
    lang = get_lang(message.chat.id)
    if message.text == translations[lang]['back']:
        start(message)
        return
    if message.chat.id in user_state and user_state[message.chat.id] == 'registering':
        bot.send_message(message.chat.id, "Siz allaqachon ro'yxatdan o'tish jarayonidasiz.")
        return
    user_state[message.chat.id] = 'registering'
    msg = bot.send_message(message.chat.id, translations[lang]['enter_name'], reply_markup=back_button(message.chat.id))
    bot.register_next_step_handler(msg, process_name_step)

def process_name_step(message):
    if message.text == translations[get_lang(message.chat.id)]['back']:
        start(message)
        return
    chat_id = message.chat.id
    name = message.text
    conn = sqlite3.connect('office_bot.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO users (user_id, first_name, registered_at) VALUES (?, ?, ?)",
                   (chat_id, name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

    user_state[chat_id] = 'awaiting_phone'
    lang = get_lang(chat_id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton(translations[lang]['phone_button'], request_contact=True))
    markup.add(translations[lang]['back'])
    bot.send_message(chat_id, translations[lang]['phone_request'], reply_markup=markup)
    bot.register_next_step_handler(message, process_phone_step, name)

def process_phone_step(message, name):
    if message.text == translations[get_lang(message.chat.id)]['back']:
        start(message)
        return
    chat_id = message.chat.id
    phone = None

    # Kontakt yoki matn sifatida
    if message.contact:
        phone = message.contact.phone_number
    elif message.text:
        raw = message.text.strip()
        if raw.startswith('+') and raw[1:].isdigit() and len(raw) in [12, 13]:
            phone = raw if raw.startswith('+') else '+' + raw

    # Formatni tekshirish
    if not phone or not (phone.startswith('+998') and len(phone) in [12, 13]):
        lang = get_lang(chat_id)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(types.KeyboardButton(translations[lang]['phone_button'], request_contact=True))
        markup.add(translations[lang]['back'])
        msg = bot.send_message(chat_id, translations[lang]['invalid_phone'], reply_markup=markup)
        bot.register_next_step_handler(msg, process_phone_step, name)
        return

    # Saqlash
    conn = sqlite3.connect('office_bot.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET phone=? WHERE user_id=?", (phone, chat_id))
    conn.commit()
    conn.close()

    # Yakunlash
    lang = get_lang(chat_id)
    response = translations[lang]['registered'].format(name, phone)
    bot.send_message(chat_id, response, reply_markup=main_menu(chat_id))
    bot.send_message(ADMIN_ID, translations[lang]['new_user'].format(name, phone, chat_id))

# Murojaat yuborish
@bot.message_handler(func=lambda m: m.text in ["📥 Murojaat yuborish", "📥 Отправить запрос"])
def request_file(message):
    lang = get_lang(message.chat.id)
    msg = bot.send_message(message.chat.id,
                         "📎 Iltimos, xizmat turini yozing:" if lang == 'uz'
                         else "📎 Пожалуйста, укажите вид услуги:",
                         reply_markup=back_button(message.chat.id))
    bot.register_next_step_handler(msg, save_and_forward_to_admin)

def save_and_forward_to_admin(message):
    if message.text == translations[get_lang(message.chat.id)]['back']:
        start(message)
        return
    chat_id = message.chat.id
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect('office_bot.db')
    cursor = conn.cursor()

    if message.content_type == 'text':
        cursor.execute("INSERT INTO messages (user_id, message_type, content, sent_at) VALUES (?, ?, ?, ?)",
                       (chat_id, 'text', message.text, now))
        bot.send_message(ADMIN_ID,
                       f"✉️ Yangi xabar:\n👤 Foydalanuvchi: {chat_id}\n📝 {message.text}\n⏰ {now}",
                       reply_markup=generate_reply_markup(chat_id))

    elif message.content_type == 'photo':
        file_id = message.photo[-1].file_id
        cursor.execute("INSERT INTO messages (user_id, message_type, content, file_id, sent_at) VALUES (?, ?, ?, ?, ?)",
                       (chat_id, 'photo', message.caption or '', file_id, now))
        bot.send_photo(ADMIN_ID, file_id,
                     caption=f"📷 Yangi rasm:\n👤 Foydalanuvchi: {chat_id}\n📝 {message.caption or ''}\n⏰ {now}",
                     reply_markup=generate_reply_markup(chat_id))

    elif message.content_type == 'document':
        file_id = message.document.file_id
        cursor.execute("INSERT INTO messages (user_id, message_type, content, file_id, sent_at) VALUES (?, ?, ?, ?, ?)",
                       (chat_id, 'document', message.caption or '', file_id, now))
        bot.send_document(ADMIN_ID, file_id,
                        caption=f"📄 Yangi fayl:\n👤 Foydalanuvchi: {chat_id}\n📝 {message.caption or ''}\n⏰ {now}",
                        reply_markup=generate_reply_markup(chat_id))

    conn.commit()
    conn.close()

    lang = get_lang(chat_id)
    bot.send_message(chat_id,
                   "✅Murojaatingiz  uchun  rahmat,biz tez orada aloqaga chiqamiz" if lang == 'uz'
                   else "✅ Спасибо за ваш запрос, мы свяжемся с вами в ближайшее время.",
                   reply_markup=main_menu(chat_id))

# Admin uchun javob tugmasi
def generate_reply_markup(user_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✍️ Javob yozish", callback_data=f"reply_{user_id}"))
    return markup

# Admin javobini qabul qilish
@bot.callback_query_handler(func=lambda call: call.data.startswith('reply_'))
def handle_reply_callback(call):
    user_id = int(call.data.split('_')[1])
    msg = bot.send_message(ADMIN_ID, f"✍️ Javob yozing (Foydalanuvchi: {user_id}):")
    bot.register_next_step_handler(msg, process_admin_reply, user_id)

def process_admin_reply(message, user_id):
    try:
        bot.send_message(user_id, f"👨‍💼 Admin javobi:\n{message.text}")
        bot.send_message(ADMIN_ID, f"✅ Javob yuborildi (ID: {user_id})")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"⚠️ Xatolik: {str(e)}\nFoydalanuvchi botni bloklagan bo'lishi mumkin.")

# Admin komandasi
@bot.message_handler(commands=['admin'])
def admin_command(message):
    if message.from_user.id == ADMIN_ID:
        lang = get_lang(message.chat.id)
        bot.send_message(message.chat.id, translations[lang]['admin_welcome'], reply_markup=admin_menu(message.chat.id))
    else:
        lang = get_lang(message.chat.id)
        bot.send_message(message.chat.id, translations[lang]['no_access'])

# Statistika
@bot.message_handler(func=lambda m: m.text in ["📊 Statistika", "📊 Статистика"] and m.from_user.id == ADMIN_ID)
def show_stats(message):
    conn = sqlite3.connect('office_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    users_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM messages")
    total_messages = cursor.fetchone()[0]
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("SELECT COUNT(*) FROM messages WHERE date(sent_at) = ?", (today,))
    today_messages = cursor.fetchone()[0]
    conn.close()
    lang = get_lang(message.chat.id)
    response = (f"📊 Bot statistikasi:\n"
                f"👥 Foydalanuvchilar: {users_count}\n"
                f"✉️ Bugungi xabarlar: {today_messages}\n"
                f"⏰ So'ngi yangilanish: {datetime.now().strftime('%H:%M')}")
    if lang == 'ru':
        response = (f"📊 Статистика бота:\n"
                    f"👥 Пользователи: {users_count}\n"
                    f"✉️ Сегодняшние сообщения: {today_messages}\n"
                    f"⏰ Последнее обновление: {datetime.now().strftime('%H:%M')}")
    bot.send_message(message.chat.id, response)

# Xabar yuborish (broadcast)
@bot.message_handler(func=lambda m: m.text in ["📢 Xabar yuborish", "📢 Отправить сообщение"] and m.from_user.id == ADMIN_ID)
def broadcast_message(message):
    lang = get_lang(message.chat.id)
    msg = bot.send_message(message.chat.id,
                         "📝 Foydalanuvchilarga(hamma) habar yuborish:" if lang == 'uz'
                         else "📝Отправить сообщение пользователям:")
    bot.register_next_step_handler(msg, process_broadcast)

def process_broadcast(message):
    conn = sqlite3.connect('office_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    conn.close()
    success = failed = 0
    for user in users:
        try:
            bot.send_message(user[0], f"📢 Admin xabari:\n{message.text}")
            success += 1
        except:
            failed += 1
    lang = get_lang(message.chat.id)
    result = (f"✅ Xabar yuborildi!\nMuvaffaqiyatli: {success}\nMuvaffaqiyatsiz: {failed}")
    if lang == 'ru':
        result = f"✅ Сообщение отправлено!\nУспешно: {success}\nНеудачно: {failed}"
    bot.send_message(message.chat.id, result)

# Orqaga qaytish
@bot.message_handler(func=lambda m: m.text in ["🔙 Orqaga qaytish", "🔙 Назад"])
def back_handler(message):
    start(message)

# Bosh menyuga qaytish (admin)
@bot.message_handler(func=lambda m: m.text in ["🏠 Bosh menyu", "🏠 Главное меню"] and m.from_user.id == ADMIN_ID)
def back_to_main_admin(message):
    start(message)

# Bog'lanish
@bot.message_handler(func=lambda m: m.text in ["📞 Bog'lanish", "📞 Контакты"])
def boglanish(message):
    lang = get_lang(message.chat.id)
    text = ("📞 Biz bilan bog'lanish:\nTelegram: @asrbux_21\nTelefon: +998 55 701 21 00\n+998 99 223 11 13"
            if lang == 'uz' else "📞 Наши контакты:\nTelegram: @asrbux_21\nТелефон: +998 55 701 21 00\n+998 99 223 11 13")
    bot.send_message(message.chat.id, text, reply_markup=main_menu(message.chat.id))

# Botni ishga tushirish
if __name__ == '__main__':
    print("Bot ishga tushdi...")
    bot.polling(none_stop=True)