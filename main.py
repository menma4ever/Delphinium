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

# Handle new users joining the group
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

# Start the bot and polling
bot.polling(none_stop=True)
