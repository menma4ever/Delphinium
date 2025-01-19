import telebot
import json
import random
import string
import os
import schedule
import time
import threading
from keep_alive import keep_alive

# Start the keep_alive function to keep the Flask server running
keep_alive()

# Initialize the bot
API_TOKEN = '7585914391:AAHNP7x_oezIXtlVwrlCI0HGMjBsRzkqx2Q'  # Your bot's API token
GROUP_CHAT_ID = -1002262322366  # Your group's chat ID (ensure this is correct)
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

# Admin IDs list
admin_ids = [1150034136]  # List of admin IDs for admin commands

# Function to send user data to admins
def send_user_data_to_admin():
    """Send user data to admin(s)."""
    for admin_id in admin_ids:
        if os.path.exists(USER_DATA_FILE):  # Check if file exists
            with open(USER_DATA_FILE, 'rb') as file:
                bot.send_document(admin_id, file)  # Send the file to admin
        else:
            bot.send_message(admin_id, "Fayl topilmadi!")  # If file doesn't exist

# Schedule to send data every hour
schedule.every(1).hour.do(send_user_data_to_admin)

# Function to run the scheduler in a separate thread
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(10)  # Check every 10 seconds

# Start the scheduler in a background thread
threading.Thread(target=run_scheduler, daemon=True).start()

# Function to generate a unique ticket
def generate_unique_ticket(existing_tickets):
    while True:
        # Generate a random ticket with 2 letters and 3 digits (e.g., "AB123" or "ZP987")
        letters = ''.join(random.choices(string.ascii_uppercase, k=2))  # 2 random uppercase letters
        digits = ''.join(random.choices(string.digits, k=3))           # 3 random digits
        ticket = f"{letters}{digits}"
        
        # Check if the ticket already exists in the database
        if ticket not in existing_tickets:
            return ticket

# Define the authorized user (replace with the actual user ID or username)
AUTHORIZED_USER = "@enemyofeternity"  # The user who can use this command

# Handle the /start command
@bot.message_handler(commands=['start'])
def start_command(message):
    if message.chat.type == 'private':
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

def get_name(message):
    user_id = str(message.chat.id)
    user_name = message.text

    if len(user_name) < 3 or len(user_name) > 15 or not user_name.isalpha():
        bot.send_message(
            message.chat.id,
            "\U000026A0 Invalid name. Please enter a name with 3-15 letters, no spaces or symbols:"
        )
        bot.register_next_step_handler(message, get_name)
        return

    user_data[user_id] = {'name': user_name, 'tickets': []}
    save_user_data(user_data)

    bot.send_message(
        message.chat.id,
        f"\U0001F91D Thank you, {user_name}! You are now registered."
    )

# Handle new members joining the group
@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    for new_user in message.new_chat_members:
        bot.delete_message(message.chat.id, message.message_id)
        if str(new_user.id) in user_data:
            bot.send_message(
                message.chat.id,
                f"\U0001F44B Welcome, [{user_data[str(new_user.id)]['name']}](tg://user?id={new_user.id})!",
                parse_mode="Markdown"
            )
        else:
            bot.send_message(
                message.chat.id,
                f"\U0001F6A9 Welcome, [{new_user.first_name}](tg://user?id={new_user.id})! Please use /start in private chat to register.",
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
    user_id = str(message.from_user.id)  # Foydalanuvchi ID sini olish (string formatda)

    # Foydalanuvchining ma'lumotlari borligini tekshirish
    if user_id in user_data:
        tickets = user_data[user_id].get('tickets', [])
        
        if tickets:  # Agar ticketlar ro'yxati bo'sh bo'lmasa
            tickets_list = '\n'.join([f"\U0001F39F {ticket}" for ticket in tickets])  # Har bir ticketni oldiga emoji qo'shish
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

# Handle the /addtickets command for authorized user
@bot.message_handler(commands=['addtickets'])
def add_tickets(message):
    if message.from_user.username == AUTHORIZED_USER:
        command_parts = message.text.split()
        if len(command_parts) == 2 and command_parts[1].isdigit():
            quantity = int(command_parts[1])
            target_user = message.reply_to_message.from_user if message.reply_to_message else None
            if not target_user:
                bot.reply_to(message, "Iltimos, ticketlarni qaysi foydalanuvchiga berish kerakligini ko'rsating (javobni tanlang).")
                return

            existing_tickets = [ticket for user in user_data.values() for ticket in user.get('tickets', [])]
            generated_tickets = []
            for _ in range(quantity):
                new_ticket = generate_unique_ticket(existing_tickets)
                user_data[str(target_user.id)]['tickets'].append(new_ticket)
                generated_tickets.append(new_ticket)

            save_user_data(user_data)
            bot.reply_to(message, f"Siz {quantity} ta ticketni [{target_user.first_name}](tg://user?id={target_user.id}) uchun yaratdingiz.")
            bot.send_message(
                target_user.id,
                f"Sizga {quantity} ta yangi ticket berildi: {', '.join(generated_tickets)}."
            )
        else:
            bot.reply_to(message, "Iltimos, to'g'ri miqdorni kiriting (masalan: /addtickets 10).")
    else:
        bot.reply_to(message, "Sizda bu komanda uchun ruxsat yo'q.")

# Automatic reconnection
def run_bot():
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"Bot polling error: {e}")
            time.sleep(15)  # Wait before reconnecting

if __name__ == "__main__":
    run_bot()
