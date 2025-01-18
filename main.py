import telebot
import json
import random

# Initialize the bot
API_TOKEN = '7585914391:AAHNP7x_oezIXtlVwrlCI0HGMjBsRzkqx2Q'
GROUP_CHAT_ID = -1002262322366
bot = telebot.TeleBot(API_TOKEN)

# Load or initialize user data
USER_DATA_FILE = 'user_delp.json'


def load_user_data():
    """Load user data from the JSON file."""
    try:
        with open(USER_DATA_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_user_data(data):
    """Save user data to the JSON file."""
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)


# Load existing user data
user_data = load_user_data()


# Generate a unique ticket
import random
import string


import os

import os

import os
import schedule
import time

# Adminlar ID ro'yxati
admin_ids = [1150034136]

# Fayl yo'li
USER_DATA_FILE = 'user_delp.json'

def send_user_data_to_admin():
    # Har bir admin uchun fayl yuborish
    for admin_id in admin_ids:
        if os.path.exists(USER_DATA_FILE):  # Fayl mavjudligini tekshirish
            with open(USER_DATA_FILE, 'rb') as file:
                bot.send_document(admin_id, file)  # Faylni yuborish
        else:
            bot.send_message(admin_id, "Fayl topilmadi!")

# Har 1 soatda bir marta faylni yuborish uchun jadval yaratish
schedule.every(1).hour.do(send_user_data_to_admin)

@bot.message_handler(commands=['import'])
def import_user_data(message):
    # Foydalanuvchi private chatda bo'lishini tekshirish
    if message.chat.type == 'private':
        user_id = message.from_user.id  # Foydalanuvchi ID sini olish

        # Faqatgina administratorlar uchun /import komandasi
        if user_id in admin_ids:
            if os.path.exists(USER_DATA_FILE):  # Fayl mavjudligini tekshirish
                with open(USER_DATA_FILE, 'rb') as file:
                    bot.send_document(message.chat.id, file)  # Faylni yuborish
            else:
                bot.send_message(message.chat.id, "Fayl topilmadi!")
        else:
            bot.send_message(message.chat.id, "Sizda bu komanda uchun ruxsat yo'q.")
    else:
        bot.send_message(message.chat.id, "Bu komanda faqat private chatda ishlaydi.")

# Botni ishga tushirish va jadvalni tekshirish
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(10)  # Har 1 minutda jadvalni tekshiradi

# Boshqa kodlar va botni ishga tushirish
import threading
threading.Thread(target=run_scheduler, daemon=True).start()

bot.polling(none_stop=True)



def generate_unique_ticket(existing_tickets):
    while True:
        # Generate a random ticket with 2 letters and 3 digits (e.g., "AB123" or "ZP987")
        letters = ''.join(random.choices(string.ascii_uppercase, k=2))  # 2 random uppercase letters
        digits = ''.join(random.choices(string.digits, k=3))           # 3 random digits
        ticket = f"{letters}{digits}"
        
        # Check if the ticket already exists in the database
        if ticket not in existing_tickets:
            return ticket


@bot.message_handler(content_types=['new_chat_members'])
def handle_addition(message):
    added_by = message.from_user  # Who added the new users
    new_users = message.new_chat_members  # List of newly added users

    # Delete the join message in the group
    bot.delete_message(message.chat.id, message.message_id)

    # Load existing tickets
    existing_tickets = [ticket for user in user_data.values() for ticket in user.get('tickets', [])]

    # Check if the user who added new members exists in the database
    if str(added_by.id) not in user_data:
        user_data[str(added_by.id)] = {
            'name': added_by.first_name,
            'tickets': []
        }

    # Generate a ticket for the user who added new members
    new_ticket = generate_unique_ticket(existing_tickets)
    user_data[str(added_by.id)]['tickets'].append(new_ticket)
    save_user_data(user_data)

    # Generate links for the new users
    new_user_links = ", ".join(
        [f"[{user.first_name}](tg://user?id={user.id})" for user in new_users]
    )

    # Link for the user who added new members
    added_by_link = f"[{added_by.first_name}](tg://user?id={added_by.id})"

    # Notify the group about the addition
    bot.send_message(
        message.chat.id,
        f"\U0001F44B {new_user_links} guruhga qo'shildi! Ularni {added_by_link} qo'shdi. {added_by.first_name}, sizga yangi ticket berildi: `{new_ticket}`.",
        parse_mode="Markdown"
    )

    # Notify the user who added the members in private chat
    bot.send_message(
        added_by.id,
        f"\U0001F4B0 Siz {len(new_users)} kishini guruhga qo'shdingiz. Sizning yangi ticketingiz: {new_ticket}."
    )

    # Notify each new user in private chat
    for new_user in new_users:
        # Tekshirish: foydalanuvchi ma'lumotlar bazasida mavjudmi?
        if str(new_user.id) not in user_data:
            # Add the new user to the database
            user_data[str(new_user.id)] = {
                'name': new_user.first_name,
                'tickets': []
            }
            save_user_data(user_data)

        try:
            # Send a welcome message to the new user in private chat
            bot.send_message(
                new_user.id,
                f"\U0001F44B Salom, [{new_user.first_name}](tg://user?id={new_user.id})! Siz guruhga qo'shildingiz. "
                f"Botdan foydalanish uchun xususiy chatda /start buyrug'ini kiriting.",
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Xabar yuborishda xatolik yuz berdi: {e}")

# Command to handle /start
@bot.message_handler(commands=['start'])
def start_command(message):
    if message.chat.type == 'private':
        # Foydalanuvchi allaqachon `user_data` ichida mavjudligini tekshirish
        if str(message.chat.id) in user_data:
            user_name = user_data[str(message.chat.id)]['name']
            bot.send_message(
                message.chat.id,
                f"\U0001F4A1 You are already registered as {user_name}."
            )
        else:
            bot.send_message(
                message.chat.id,
                "\U0001F338 Hello! Please provide your name (3-15 letters, no spaces or symbols):"
            )
            bot.register_next_step_handler(message, get_name)
    else:
        bot.send_message(
            message.chat.id,
            "\U0001F338 I am Delphinium, your group assistant bot!"
        )


def get_name(message):
    name = message.text.strip()
    # Foydalanuvchi ma'lumotlar bazasida mavjudligini tekshirish
    if str(message.chat.id) in user_data:
        bot.send_message(
            message.chat.id,
            "\U0001F4A1 You are already registered."
        )
        return

    # Ismni tekshirish
    if 3 <= len(name) <= 15 and name.isalpha():
        user_data[str(message.chat.id)] = {
            'name': name,
            'age': None,
            'tickets': []
        }
        save_user_data(user_data)
        bot.send_message(
            message.chat.id,
            f"\U0001F389 Welcome, {name}! Please provide your age:"
        )
        bot.register_next_step_handler(message, get_age)
    else:
        bot.send_message(
            message.chat.id,
            "\U0001F6AB Invalid name. Please provide a valid name (3-15 letters, no spaces or symbols):"
        )
        bot.register_next_step_handler(message, get_name)


def get_age(message):
    try:
        age = int(message.text.strip())
        if str(message.chat.id) not in user_data:
            bot.send_message(
                message.chat.id,
                "\U0001F6AB Please use /start to begin the registration process."
            )
            return

        if 0 < age <= 120:
            user_data[str(message.chat.id)]['age'] = age
            save_user_data(user_data)
            bot.send_message(
                message.chat.id,
                "\U0001F64C Registration complete!"
            )
        else:
            bot.send_message(
                message.chat.id,
                "\U0001F6AB Invalid age. Please provide a valid age:"
            )
            bot.register_next_step_handler(message, get_age)
    except ValueError:
        bot.send_message(
            message.chat.id,
            "\U0001F6AB Invalid age. Please provide a valid age:"
        )
        bot.register_next_step_handler(message, get_age)


# Load and save user data functions
def load_user_data():
    """Load user data from the JSON file."""
    try:
        with open(USER_DATA_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_user_data(data):
    """Save user data to the JSON file."""
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)


# Load existing user data
user_data = load_user_data()

# Handle new members joining the group
@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    for new_user in message.new_chat_members:
        bot.delete_message(message.chat.id, message.message_id)
        if new_user.id in user_data:
            bot.send_message(
                message.chat.id,
                f"\U0001F44B Welcome, [{user_data[new_user.id]['name']}](tg://user?id={new_user.id})!",
                parse_mode="Markdown"
            )
        else:
            bot.send_message(
                message.chat.id,
                f"\U0001F6A9 Welcome, [{new_user.first_name}](tg://user?id={new_user.id})! Please use /start in private chat to register.",
                parse_mode="Markdown"
            )

import json

USER_DATA_FILE = 'user_delp.json'

# Foydalanuvchi ma'lumotlarini yuklash
def load_user_data():
    try:
        with open(USER_DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Foydalanuvchi ma'lumotlarini saqlash
def save_user_data(data):
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@bot.message_handler(commands=['mytickets'])
def show_tickets(message):
    user_id = str(message.from_user.id)  # Foydalanuvchi ID sini olish (string formatda)

    # Foydalanuvchining ma'lumotlari borligini tekshirish
    if user_id in user_data:
        tickets = user_data[user_id].get('tickets', [])
        
        if tickets:  # Agar ticketlar ro'yxati bo'sh bo'lmasa
            tickets_list = '\n'.join([f"🎟 {ticket}" for ticket in tickets])  # Har bir ticketni oldiga emoji qo'shish
            bot.reply_to(
                message,
                f"Sizning ticketlaringiz:\n{tickets_list}"
            )
        else:
            bot.reply_to(
                message,
                "Sizda hech qanday ticket yo'q."
            )
    else:
        bot.reply_to(
            message,
            "Sizda hech qanday ticket yo'q."
        )


# Start the bot
bot.polling(none_stop=True)