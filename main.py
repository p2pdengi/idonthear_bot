import os
import telebot
from datetime import datetime
import json
import time

# ========== НАСТРОЙКИ ==========
BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    BOT_TOKEN = "8787648063:AAFrdzHvfOMRKSe7_5QeikzWv3sJhE-f5wg"  # для локального запуска

ADMIN_IDS = [
    1076138305,   # Мой айди
    8210821362,   # ID Вари
    6378930858,   # ID вики
]

# Файл для хранения заблокированных пользователей и их сообщений
BANNED_FILE = "banned_users.json"

WELCOME_TEXT = """
❗️ПЕРЕД ПОЛЬЗОВАНИЕМ ПРОЧТИТЕ ПРАВИЛА В ТГК❗️

Я создатель или админ подслушано 89 школа, напиши мне свою сплетню или сокровенную вещь которой хочешь поделится со школой.

❗️ОБЩЕНИЕ С АДМИНАМИ ЧЕРЕЗ БОТА НЕВОЗМОЖНО - ВАМ НЕ ОТВЕТЯТ❗️

❗️Если вы хотите опубликовать сплетню, добавляйте в конце "#подслушано" иначе НЕ ОПУБЛИКУЕМ❗️

Также, если хотите, можете добавить снизу своё имя и класс, если НЕ хотите, чтобы было опубликовано анонимно.

Канал, где публикуют: https://t.me/anonimnajaww
"""
# ===============================

bot = telebot.TeleBot(BOT_TOKEN)
time.sleep(2)
bot.remove_webhook()

# ===== ФУНКЦИИ ДЛЯ РАБОТЫ С БАН-ЛИСТОМ =====

def load_banned_users():
    """Загружает список забаненных пользователей из файла"""
    if os.path.exists(BANNED_FILE):
        with open(BANNED_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_banned_users(banned_data):
    """Сохраняет список забаненных пользователей в файл"""
    with open(BANNED_FILE, 'w', encoding='utf-8') as f:
        json.dump(banned_data, f, ensure_ascii=False, indent=2)

def is_user_banned(user_id):
    """Проверяет, забанен ли пользователь"""
    banned = load_banned_users()
    return str(user_id) in banned

def add_banned_user(user_id, username=None):
    """Добавляет пользователя в бан-лист"""
    banned = load_banned_users()
    banned[str(user_id)] = {
        "username": username or "Неизвестно",
        "banned_date": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "messages": []
    }
    save_banned_users(banned)

def remove_banned_user(user_id):
    """Удаляет пользователя из бан-листа"""
    banned = load_banned_users()
    if str(user_id) in banned:
        del banned[str(user_id)]
        save_banned_users(banned)
        return True
    return False

def add_banned_message(user_id, message_text):
    """Добавляет сообщение забаненного пользователя в историю"""
    banned = load_banned_users()
    user_id_str = str(user_id)
    if user_id_str in banned:
        banned[user_id_str]["messages"].append({
            "text": message_text,
            "date": datetime.now().strftime("%d.%m.%Y %H:%M")
        })
        save_banned_users(banned)

def get_banned_messages(user_id):
    """Возвращает сообщения забаненного пользователя"""
    banned = load_banned_users()
    return banned.get(str(user_id), {}).get("messages", [])

# ===== КОМАНДЫ ДЛЯ АДМИНОВ =====

@bot.message_handler(commands=['banuserid'])
def ban_user(message):
    """Бан пользователя: /banuserid 123456789"""
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "❌ У вас нет прав для этой команды!")
        return
    
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "❌ Используйте: /banuserid 123456789")
            return
        
        user_id = int(parts[1])
        
        if is_user_banned(user_id):
            bot.reply_to(message, f"⚠️ Пользователь с ID {user_id} уже в бане!")
            return
        
        username = None
        try:
            chat = bot.get_chat(user_id)
            username = chat.username or chat.first_name
        except:
            username = str(user_id)
        
        add_banned_user(user_id, username)
        bot.reply_to(message, f"✅ Пользователь {username} (ID: {user_id}) добавлен в бан-лист!")
        
    except ValueError:
        bot.reply_to(message, "❌ ID должен быть числом!")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {e}")

@bot.message_handler(commands=['unbanuserid'])
def unban_user(message):
    """Разбан пользователя: /unbanuserid 123456789"""
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "❌ У вас нет прав для этой команды!")
        return
    
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "❌ Используйте: /unbanuserid 123456789")
            return
        
        user_id = int(parts[1])
        
        if not is_user_banned(user_id):
            bot.reply_to(message, f"⚠️ Пользователь с ID {user_id} не в бане!")
            return
        
        banned = load_banned_users()
        username = banned[str(user_id)].get("username", str(user_id))
        
        remove_banned_user(user_id)
        bot.reply_to(message, f"✅ Пользователь {username} (ID: {user_id}) удалён из бан-листа!")
        
    except ValueError:
        bot.reply_to(message, "❌ ID должен быть числом!")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {e}")

@bot.message_handler(commands=['listbanuserid'])
def list_banned_users(message):
    """Список забаненных пользователей"""
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "❌ У вас нет прав для этой команды!")
        return
    
    banned = load_banned_users()
    
    if not banned:
        bot.reply_to(message, "📋 В бан-листе никого нет.")
        return
    
    text = "🚫 **СПИСОК ЗАБАНЕННЫХ ПОЛЬЗОВАТЕЛЕЙ:**\n\n"
    for user_id, data in banned.items():
        username = data.get("username", "Неизвестно")
        banned_date = data.get("banned_date", "Неизвестно")
        msg_count = len(data.get("messages", []))
        text += f"• ID: {user_id} (@{username})\n  📅 Забанен: {banned_date}\n  💬 Сообщений в бане: {msg_count}\n\n"
    
    bot.reply_to(message, text)

@bot.message_handler(commands=['messagesbanuserid'])
def get_banned_messages_command(message):
    """Сообщения забаненного пользователя: /messagesbanuserid 123456789"""
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "❌ У вас нет прав для этой команды!")
        return
    
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "❌ Используйте: /messagesbanuserid 123456789")
            return
        
        user_id = int(parts[1])
        
        if not is_user_banned(user_id):
            bot.reply_to(message, f"⚠️ Пользователь с ID {user_id} не в бане!")
            return
        
        messages = get_banned_messages(user_id)
        
        if not messages:
            bot.reply_to(message, f"📋 У пользователя с ID {user_id} нет сообщений в бане.")
            return
        
        banned = load_banned_users()
        username = banned[str(user_id)].get("username", str(user_id))
        
        text = f"📩 **СООБЩЕНИЯ ПОЛЬЗОВАТЕЛЯ {username} (ID: {user_id}) ВО ВРЕМЯ БАНА:**\n\n"
        for i, msg in enumerate(messages, 1):
            text += f"{i}. [{msg['date']}] {msg['text']}\n"
        
        if len(text) > 4096:
            for x in range(0, len(text), 4096):
                bot.reply_to(message, text[x:x+4096])
        else:
            bot.reply_to(message, text)
        
    except ValueError:
        bot.reply_to(message, "❌ ID должен быть числом!")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {e}")

# ===== ОСНОВНАЯ ФУНКЦИЯ ДЛЯ ОБЫЧНЫХ ПОЛЬЗОВАТЕЛЕЙ =====

def send_to_admins_regular(message, media_type, media_content):
    """Отправка сообщений от обычных пользователей (с данными об отправителе)"""
    user = message.from_user
    
    # Проверяем бан
    if is_user_banned(user.id):
        text = message.caption or message.text or "Медиафайл"
        add_banned_message(user.id, text)
        return
    
    sender = f"@{user.username}" if user.username else user.first_name
    date = datetime.fromtimestamp(message.date).strftime("%d.%m.%Y %H:%M")
    
    caption = message.caption or ""
    has_hashtag = "#подслушано" in caption.lower()
    
    for admin_id in ADMIN_IDS:
        try:
            # Отправляем медиафайл
            if media_type == "photo":
                sent_msg = bot.send_photo(
                    chat_id=admin_id,
                    photo=media_content,
                    caption=caption if caption else "📸 Фото без подписи"
                )
            elif media_type == "video":
                sent_msg = bot.send_video(
                    chat_id=admin_id,
                    video=media_content,
                    caption=caption if caption else "🎬 Видео без подписи"
                )
            elif media_type == "document":
                sent_msg = bot.send_document(
                    chat_id=admin_id,
                    document=media_content,
                    caption=caption if caption else "📄 Документ без подписи"
                )
            elif media_type == "audio":
                sent_msg = bot.send_audio(
                    chat_id=admin_id,
                    audio=media_content,
                    caption=caption if caption else "🎵 Аудио без подписи"
                )
            elif media_type == "voice":
                sent_msg = bot.send_voice(
                    chat_id=admin_id,
                    voice=media_content,
                    caption=caption if caption else "🎤 Голосовое сообщение"
                )
            elif media_type == "animation":
                sent_msg = bot.send_animation(
                    chat_id=admin_id,
                    animation=media_content,
                    caption=caption if caption else "🎥 GIF без подписи"
                )
            else:
                sent_msg = bot.send_message(
                    chat_id=admin_id,
                    text=f"📎 Получен файл неизвестного типа\n\n{caption if caption else 'Без подписи'}"
                )
                media_type = "text"
            
            # Отправляем данные об отправителе
            info_text = (
                f"👤 Отправитель: {sender}\n"
                f"🆔 ID: {user.id}\n"
                f"📅 Дата: {date}\n"
                f"📁 Тип: {media_type}\n"
                f"🏷️ Хэштег #подслушано: {'✅ ЕСТЬ' if has_hashtag else '❌ НЕТ'}"
            )
            
            bot.send_message(
                chat_id=admin_id,
                text=info_text,
                reply_to_message_id=sent_msg.message_id
            )
            
        except Exception as e:
            print(f"⚠️ Ошибка при отправке админу {admin_id}: {e}")
    
    # Ответ пользователю (напоминание про хэштег)
    if has_hashtag:
        bot.reply_to(message, "✅ Сообщение отправлено! Оно будет опубликовано после проверки в канале!")
    else:
        bot.reply_to(message, "⚠️ Вы забыли добавить #подслушано! Сообщение НЕ будет опубликовано.")

# ===== ОТПРАВКА СООБЩЕНИЙ ОТ АДМИНОВ =====

def send_to_admins_admin(message, media_type, media_content):
    """Отправка сообщений от админов (одним сообщением, без напоминания про хэштег)"""
    user = message.from_user
    sender = f"@{user.username}" if user.username else user.first_name
    
    for admin_id in ADMIN_IDS:
        try:
            if media_type == "text":
                # Для текста - одно сообщение с указанием отправителя
                formatted_text = f"{message.text} ({sender})"
                bot.send_message(
                    chat_id=admin_id,
                    text=formatted_text
                )
            else:
                # Для медиа - отправляем с подписью
                caption = message.caption or ""
                media_caption = f"{caption} ({sender})" if caption else f"📎 Файл от админа ({sender})"
                
                if media_type == "photo":
                    bot.send_photo(chat_id=admin_id, photo=media_content, caption=media_caption)
                elif media_type == "video":
                    bot.send_video(chat_id=admin_id, video=media_content, caption=media_caption)
                elif media_type == "document":
                    bot.send_document(chat_id=admin_id, document=media_content, caption=media_caption)
                elif media_type == "audio":
                    bot.send_audio(chat_id=admin_id, audio=media_content, caption=media_caption)
                elif media_type == "voice":
                    bot.send_voice(chat_id=admin_id, voice=media_content, caption=media_caption)
                elif media_type == "animation":
                    bot.send_animation(chat_id=admin_id, animation=media_content, caption=media_caption)
                    
        except Exception as e:
            print(f"⚠️ Ошибка при отправке админу {admin_id}: {e}")

# ===== ОБРАБОТЧИКИ СООБЩЕНИЙ =====

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    """Обработка фото"""
    photo = message.photo[-1]
    if message.from_user.id in ADMIN_IDS:
        send_to_admins_admin(message, "photo", photo.file_id)
    else:
        send_to_admins_regular(message, "photo", photo.file_id)

@bot.message_handler(content_types=['video'])
def handle_video(message):
    """Обработка видео"""
    if message.from_user.id in ADMIN_IDS:
        send_to_admins_admin(message, "video", message.video.file_id)
    else:
        send_to_admins_regular(message, "video", message.video.file_id)

@bot.message_handler(content_types=['document'])
def handle_document(message):
    """Обработка документов"""
    if message.from_user.id in ADMIN_IDS:
        send_to_admins_admin(message, "document", message.document.file_id)
    else:
        send_to_admins_regular(message, "document", message.document.file_id)

@bot.message_handler(content_types=['audio'])
def handle_audio(message):
    """Обработка аудио"""
    if message.from_user.id in ADMIN_IDS:
        send_to_admins_admin(message, "audio", message.audio.file_id)
    else:
        send_to_admins_regular(message, "audio", message.audio.file_id)

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    """Обработка голосовых сообщений"""
    if message.from_user.id in ADMIN_IDS:
        send_to_admins_admin(message, "voice", message.voice.file_id)
    else:
        send_to_admins_regular(message, "voice", message.voice.file_id)

@bot.message_handler(content_types=['animation'])
def handle_animation(message):
    """Обработка GIF"""
    if message.from_user.id in ADMIN_IDS:
        send_to_admins_admin(message, "animation", message.animation.file_id)
    else:
        send_to_admins_regular(message, "animation", message.animation.file_id)

@bot.message_handler(content_types=['text'])
def handle_text(message):
    """Обработка текстовых сообщений"""
    user = message.from_user
    
    # Если это админ
    if user.id in ADMIN_IDS:
        # Проверяем, не команда ли это
        if message.text.startswith('/'):
            return
        
        sender = f"@{user.username}" if user.username else user.first_name
        formatted_text = f"{message.text} ({sender})"
        
        for admin_id in ADMIN_IDS:
            try:
                bot.send_message(chat_id=admin_id, text=formatted_text)
            except Exception as e:
                print(f"⚠️ Ошибка при отправке админу {admin_id}: {e}")
        return
    
    # Если это обычный пользователь
    if is_user_banned(user.id):
        add_banned_message(user.id, message.text)
        return
    
    sender = f"@{user.username}" if user.username else user.first_name
    date = datetime.fromtimestamp(message.date).strftime("%d.%m.%Y %H:%M")
    has_hashtag = "#подслушано" in message.text.lower()
    
    for admin_id in ADMIN_IDS:
        try:
            # Первое сообщение: Текст сплетни
            first_msg = bot.send_message(
                chat_id=admin_id,
                text=f"{message.text}"
            )
            
            # Второе сообщение: Данные об отправителе
            info_text = (
                f"👤 Отправитель: {sender}\n"
                f"🆔 ID: {user.id}\n"
                f"📅 Дата: {date}\n"
                f"🏷️ Хэштег #подслушано: {'✅ ЕСТЬ' if has_hashtag else '❌ НЕТ'}"
            )
            
            bot.send_message(
                chat_id=admin_id,
                text=info_text,
                reply_to_message_id=first_msg.message_id
            )
            
        except Exception as e:
            print(f"⚠️ Ошибка при отправке админу {admin_id}: {e}")
    
    # Ответ пользователю (напоминание про хэштег)
    if has_hashtag:
        bot.reply_to(message, "✅ Сообщение отправлено! Оно будет опубликовано после проверки в канале!")
    else:
        bot.reply_to(message, "⚠️ Вы забыли добавить #подслушано! Сообщение НЕ будет опубликовано.")

if __name__ == "__main__":
    print("🤖 Бот для Подслушано 89 школа запущен!")
    print("👥 Админов:", len(ADMIN_IDS))
    print("📋 Команды администратора:")
    print("  /banuserid <id> - забанить пользователя")
    print("  /unbanuserid <id> - разбанить пользователя")
    print("  /listbanuserid - список забаненных")
    print("  /messagesbanuserid <id> - сообщения забаненного")
    bot.infinity_polling()
