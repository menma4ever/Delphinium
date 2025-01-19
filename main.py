import telebot
import json
import random
import string
import os
import schedule
import time
import threading
from flask import Flask
import sys
from telegram import ChatPermissions
from telegram.ext import CommandHandler, MessageHandler, filters
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from keep_alive import keep_alive
keep_alive()

# from keep_alive import keep_alive  # Import the keep_alive function from the separate module

# Initialize the bot
API_TOKEN = '7585914391:AAHNP7x_oezIXtlVwrlCI0HGMjBsRzkqx2Q'
GROUP_CHAT_ID = -1002262322366
bot = telebot.TeleBot(API_TOKEN)

# Load or initialize user data
USER_DATA_FILE = 'user_delp.json'

gif_links = {
    "start": "https://t.me/franxxbotsgarage/3",
    "mute": "https://t.me/franxxbotsgarage/10",
    "ban": "https://t.me/franxxbotsgarage/4 ",
    "warn": "https://t.me/franxxbotsgarage/9",
    "help": "https://t.me/franxxbotsgarage/11",
    "smile": "https://t.me/franxxbotsgarage/13",
    "shout": "https://t.me/franxxbotsgarage/15",}


def load_user_data():
    """Load user data from the JSON file."""
    try:
        with open(USER_DATA_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_user_data(data):
    """Save user data to the JSON file."""
    try:
        with open(USER_DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)
            print(f"Foydalanuvchi ma'lumotlari muvaffaqiyatli saqlandi!")  # Debug print
            print(f"Saqlanayotgan ma'lumotlar: {data}")  # Print the data that is being saved
    except Exception as e:
        print(f"Foydalanuvchi ma'lumotlarini saqlashda xato: {e}")


# Load existing user data
user_data = load_user_data()

# Admin IDs list
admin_ids = [1150034136]  # Your admin ID(s)

# Function to send user data to admins
def send_user_data_to_admin():
    """Send user data to admin(s)."""
    for admin_id in admin_ids:
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, 'rb') as file:
                bot.send_document(admin_id, file)
        else:
            bot.send_message(admin_id, "Fayl topilmadi!")

# Schedule to send data every hour
schedule.every(1).hour.do(send_user_data_to_admin)

# Function to run the scheduler in a separate thread
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(10)

# Start the scheduler in a background thread
threading.Thread(target=run_scheduler, daemon=True).start()

# Function to generate a unique ticket
def generate_unique_ticket(existing_tickets):
    while True:
        letters = ''.join(random.choices(string.ascii_uppercase, k=2))
        digits = ''.join(random.choices(string.digits, k=3))
        ticket = f"{letters}{digits}"
        
        if ticket not in existing_tickets:
            return ticket

# Handle the /start command
@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    for new_user in message.new_chat_members:
        bot.delete_message(message.chat.id, message.message_id)
        user_id = str(new_user.id)

        # Identify the user who added the new member
        added_by_user = message.from_user.id

        # Debugging: Print user joining information
        print(f"Yangi foydalanuvchi qo'shildi: {new_user.first_name}, ID: {new_user.id} - Qo'shgan: {added_by_user}")

        # Check if the user who added the new user exists in the data
        if str(added_by_user) not in user_data:
            user_data[str(added_by_user)] = {'name': message.from_user.first_name, 'tickets': []}

        # Generate and assign tickets to the user who added the new member
        existing_tickets = [ticket for user in user_data.values() for ticket in user.get('tickets', [])]
        generated_tickets = []

        # Debug: Check the existing tickets before generation
        print(f"Yangi ticketlarni yaratishdan oldin mavjud ticketlar: {existing_tickets}")

        for _ in range(1):  # Assign 5 tickets to the user who added the new member
            new_ticket = generate_unique_ticket(existing_tickets)
            user_data[str(added_by_user)]['tickets'].append(new_ticket)
            generated_tickets.append(new_ticket)

        # Save the updated user data
        save_user_data(user_data)

        # Debug: Print the user data for the one who added the new user
        print(f"Foydalanuvchi {message.from_user.first_name} uchun yaratilgan ticketlar: {generated_tickets}")
        print(f"Yangilangan foydalanuvchi ma'lumotlari: {user_data[str(added_by_user)]}")

        # Notify the group that the new user has joined and who added them
        bot.send_message(
            message.chat.id,
            f"\U0001F44B Salom, [{new_user.first_name}](tg://user?id={new_user.id})! "
            f"Qo'shgan: [{message.from_user.first_name}](tg://user?id={added_by_user}). "
            f"Sizga {len(generated_tickets)} ta ticket berildi: {', '.join(generated_tickets)}.",
            parse_mode="Markdown"
        )

# Handle the /import command to send user data to the admin
@bot.message_handler(commands=['import'])
def import_user_data(message):
    if message.chat.type == 'private':
        user_id = message.from_user.id
        if user_id in admin_ids:
            if os.path.exists(USER_DATA_FILE):  
                with open(USER_DATA_FILE, 'rb') as file:
                    bot.send_document(message.chat.id, file)
            else:
                bot.send_message(message.chat.id, "Fayl topilmadi!")
        else:
            bot.send_message(message.chat.id, "Sizda bu komanda uchun ruxsat yo'q.")
    else:
        bot.send_message(message.chat.id, "Bu komanda faqat private chatda ishlaydi.")

# Handle the /mytickets command
@bot.message_handler(commands=['mytickets'])
def show_tickets(message):
    user_id = str(message.from_user.id)
    if user_id in user_data:
        tickets = user_data[user_id].get('tickets', [])
        if tickets:
            tickets_list = '\n'.join([f"\U0001F39F {ticket}" for ticket in tickets])
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
            "Siz tizimga kirmagansiz. Iltimos, admin bilan bog'laning."
        )

# Handle the /addtickets command for admin users
@bot.message_handler(commands=['addtickets'])
def add_tickets(message):
    user_id = message.from_user.id
    if user_id in admin_ids:
        command_parts = message.text.split()
        
        if len(command_parts) == 2 and command_parts[1].isdigit():
            quantity = int(command_parts[1])

            target_user = message.reply_to_message.from_user if message.reply_to_message else None
            if not target_user:
                bot.send_message(message.chat.id, "Iltimos, ticketlarni qaysi foydalanuvchiga berish kerakligini ko'rsating (javobni tanlang).")
                return

            # Check if the target user exists in user_data, if not, initialize the user data
            if str(target_user.id) not in user_data:
                user_data[str(target_user.id)] = {'name': target_user.first_name, 'tickets': []}
            
            existing_tickets = [ticket for user in user_data.values() for ticket in user.get('tickets', [])]
            
            generated_tickets = []
            for _ in range(quantity):
                new_ticket = generate_unique_ticket(existing_tickets)
                user_data[str(target_user.id)]['tickets'].append(new_ticket)
                generated_tickets.append(new_ticket)
            
            save_user_data(user_data)

            # Debug: Print updated user data
            print(f"Yangilangan foydalanuvchi ma'lumotlari {target_user.id}: {user_data[str(target_user.id)]}")

            bot.send_message(message.chat.id, f"Siz {quantity} ta ticketni [{target_user.first_name}](tg://user?id={target_user.id}) uchun yaratdingiz.", parse_mode="Markdown")
            
            # Notify the target user in the group chat
            bot.send_message(
                GROUP_CHAT_ID,
                f"@{target_user.username}, sizga {quantity} ta yangi ticket berildi: {', '.join(generated_tickets)}."
            )
        else:
            bot.send_message(message.chat.id, "Iltimos, to'g'ri miqdorni kiriting (masalan: /addtickets 10).")
    else:
        bot.send_message(message.chat.id, "Sizda bu komanda uchun ruxsat yo'q.")

# Handle the /start command
@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)

    if user_id in user_data:
        bot.reply_to(
            message,
            f"Salom, [{message.from_user.first_name}](tg://user?id={message.from_user.id})! 💖\n\n"
            "Men Ichigo, senga yordam berishga tayyor! 🌸\n\n"
            "Siz allaqachon ro'yxatdan o'tgansiz! Quyidagi komandalarni ishlatishingiz mumkin:\n"
            "/profile - Profil ma'lumotlaringizni ko'rish\n"
            "/mytickets - Ticketlaringizni tekshirish\n"
            "/changeinfo - Profil ma'lumotlarini yangilash"
        )
    else:
        bot.reply_to(
            message,
            f"Salom, [{message.from_user.first_name}](tg://user?id={message.from_user.id})! 💖\n\n"
            "Men Ichigo, senga yordam berishga tayyor! 🌸\n"
            "Siz hali ro'yxatdan o'tmagansiz! Iltimos, /register komandasi yordamida ro'yxatdan o'ting. "
            "Ro'yxatdan o'tganingizdan so'ng, siz boshqa funksiyalarni ham ishlatishingiz mumkin! 💪"
        )

# Handle the /register command
@bot.message_handler(commands=['register'])
def register(message):
    user_id = str(message.from_user.id)
    
    if user_id in user_data:
        bot.reply_to(message, "Siz allaqachon jamoamizdasiz! 💖")
        return

    bot.send_message(message.chat.id, "Iltimos, o'zingizning nickname'ingizni yuboring: 🥰")
    
    # Collect nickname
    @bot.message_handler(func=lambda m: m.from_user.id == message.from_user.id and not m.text.isdigit())
    def get_nickname(msg):
        nickname = msg.text
        bot.send_message(message.chat.id, "Endi, yoshini yuboring. Faqat raqam bo'lishi kerak va 116 dan katta bo'lmasin! 🎂")

        # Collect age
        @bot.message_handler(func=lambda m: m.from_user.id == message.from_user.id and m.text.isdigit())
        def get_age(msg):
            age = int(msg.text)
            if age > 116:
                bot.send_message(message.chat.id, "Yosh 116 dan katta bo'lmasligi kerak! Iltimos, to'g'ri yoshni kiriting. 😌")
                return
            
            user_data[user_id] = {'nickname': nickname, 'age': age, 'tickets': []}
            save_user_data(user_data)
            bot.send_message(message.chat.id, f"Allaqachon ro'yxatdan o'tdingiz, {nickname}! Jamoamizga xush kelibsiz! 🎉✨")

# Handle the /profile command
@bot.message_handler(commands=['profile'])
def profile(message):
    user_id = str(message.from_user.id)
    
    if user_id not in user_data:
        bot.reply_to(message, "Iltimos, avval /register komandasidan foydalanib ro'yxatdan o'ting! 🙇‍♀️")
        return

    user_info = user_data[user_id]
    tickets_count = len(user_info['tickets'])
    overall_tickets = sum(len(user['tickets']) for user in user_data.values())
    win_chance = (tickets_count / overall_tickets * 100) if overall_tickets > 0 else 0

    bot.reply_to(
        message,
        f"Profil Ma'lumotlari:\n\n"
        f"Nickname: {user_info['nickname']}\n"
        f"Yosh: {user_info['age']}\n"
        f"Tickets: {tickets_count} 🎟️\n"
        f"Yutish imkoniyati: {win_chance:.2f}% ✨"
    )

# Handle the /changeinfo command
@bot.message_handler(commands=['changeinfo'])
def change_info(message):
    user_id = str(message.from_user.id)

    if user_id not in user_data:
        bot.reply_to(message, "Iltimos, avval /register komandasidan foydalanib ro'yxatdan o'ting! 🙇‍♀️")
        return

    bot.send_message(message.chat.id, "Iltimos, yangi nickname'ingizni yuboring: 💕")

    @bot.message_handler(func=lambda m: m.from_user.id == message.from_user.id and not m.text.isdigit())
    def update_nickname(msg):
        nickname = msg.text
        bot.send_message(message.chat.id, "Endi, yangi yoshni yuboring. Iltimos, raqam kiriting. 🎂")

        @bot.message_handler(func=lambda m: m.from_user.id == message.from_user.id and m.text.isdigit())
        def update_age(msg):
            age = int(msg.text)
            if age > 116:
                bot.send_message(message.chat.id, "Yosh 116 dan katta bo'lmasligi kerak! Iltimos, to'g'ri yoshni kiriting. 😌")
                return

            user_data[user_id]['nickname'] = nickname
            user_data[user_id]['age'] = age
            save_user_data(user_data)
            bot.send_message(message.chat.id, f"Sizning ma'lumotlaringiz yangilandi, {nickname}! 💖")

# Handle the /casinobegin command   
@bot.message_handler(commands=['casinobegin'])
def casino_begin(message):
    user_id = message.from_user.id
    if user_id not in admin_ids:
        bot.send_message(message.chat.id, "Faqat adminlar bu komanda ishlatishi mumkin! ❌")
        return

    command_parts = message.text.split()
    if len(command_parts) != 2 or not command_parts[1].isdigit():
        bot.send_message(message.chat.id, "Iltimos, to'g'ri miqdorni kiriting! Misol: /casinobegin 3")
        return

    count = int(command_parts[1])
    all_tickets = [(user_id, ticket) for user_id, user_info in user_data.items() for ticket in user_info['tickets']]
    if len(all_tickets) < count:
        bot.send_message(message.chat.id, "Yeterli ticket mavjud emas. Iltimos, keyinroq qayta urinib ko'ring! 🎰")
        return

    winners = random.sample(all_tickets, count)
    winner_names = []

    for idx, (winner_id, ticket) in enumerate(winners, 1):
        winner = user_data.get(str(winner_id), {})

        winner_name = winner.get('nickname') or winner.get('name')  # Get the user's nickname or name from the user_data
        winner_username = winner.get('username')  # Get the user's username from the user_data

        if not winner_name and winner_username:
            winner_name = f"@{winner_username}"

        # If no nickname, name, or username, fall back to Telegram ID
        if not winner_name:
            winner_name = f"User ID: {winner_id}"

        hidden_mention = f"[{winner_name}](tg://user?id={winner_id})"
        
        winner_names.append(f"{idx}. {hidden_mention} (Ticket: {ticket})")

    result_message = bot.send_message(message.chat.id, "🎉 Yutuvchilar quyidagilar:\n" + "\n".join(winner_names), parse_mode='Markdown')
    bot.pin_chat_message(message.chat.id, result_message.message_id)

    # After announcing winners, provide a final message
    bot.send_message(message.chat.id, "✨ Yutuq yakunlandi! Hammasiga tabriklar! 🎉")


# Start the bot
bot.polling(none_stop=True, timeout=60)

