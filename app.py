from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from apscheduler.schedulers.background import BackgroundScheduler
import random
import datetime
import os
import database
import matcher

print("Creating database tables...")
database.create_tables()
print("Database setup complete!")

app = Flask(__name__)

# ===== WAKE ROUTE =====
@app.route("/", methods=["GET"])
def wake():
    return "Quiet Loop is awake! ❤️", 200

# ===== TWILIO CREDENTIALS =====
ACCOUNT_SID = "AC564a593b6421d0146c76da49da2ad53e"
AUTH_TOKEN = "5e4087a6660c392f29582fd9d93a4ad69"
FROM_NUMBER = "whatsapp:+14155238886"

twilio_client = Client(ACCOUNT_SID, AUTH_TOKEN)

# ===== WISDOM LIBRARY =====
wisdom = [
    "You got your own shoes — don't try fitting in other people's to match the vibe they have.",
    "I wasn't born to fit in — I was born to stand out.",
    "Why you always worried 'bout what people think? They don't even know you.",
    "It's okay to not be okay — just don't stay that way.",
    "The only person you should try to be better than is the person you were yesterday.",
    "You can't heal what you won't reveal.",
    "I'm not perfect, but I'm perfectly me.",
    "Sometimes the ones that shine the brightest are the ones that have been through the darkest storms.",
    "I don't need your validation — I know who I am.",
    "If you're not growing, you're dying.",
    "You are not a drop in the ocean. You are the entire ocean in a drop. — Rumi",
    "The wound is the place where the Light enters you. — Rumi",
    "Do not judge me by my successes, judge me by how many times I fell down and got back up. — Mandela",
    "Be the change you wish to see in the world. — Gandhi",
    "The quieter you become, the more you can hear. — Ram Dass",
    "What lies behind us and what lies before us are tiny matters compared to what lies within us. — Emerson",
    "The greatest glory in living lies not in never falling, but in rising every time we fall. — Mandela",
    "Peace comes from within. Do not seek it without. — Buddha",
    "What you do makes a difference, and you have to decide what kind of difference you want to make. — Jane Goodall",
    "The best time to plant a tree was 20 years ago. The second best time is now. — Chinese Proverb",
    "A person who never made a mistake never tried anything new. — Einstein",
    "It is not how much we have, but how much we enjoy, that makes happiness. — Spurgeon",
    "The purpose of our lives is to be happy. — Dalai Lama",
]

# ===== USER DATA =====
journal_state = {}
user_reply_store = {}

# ===== SEND MESSAGE =====
def send_whatsapp(to_number, message):
    try:
        twilio_client.messages.create(
            from_=FROM_NUMBER,
            body=message,
            to=to_number
        )
        print(f"✅ Sent to {to_number}: {message[:50]}...")
    except Exception as e:
        print(f"❌ Failed: {e}")

# ===== SAVE JOURNAL ENTRY =====
def save_journal_entry(user_number, entry_type, message):
    try:
        database.save_entry(user_number, entry_type, message)
        print(f"📖 Saved journal entry for {user_number}")
    except Exception as e:
        print(f"❌ Failed to save journal: {e}")

def save_entry_with_topic(user_number, entry_type, message, topic):
    try:
        database.save_entry_with_topic(user_number, entry_type, message, topic)
        print(f"📖 Saved entry with topic '{topic}' for {user_number}")
    except Exception as e:
        print(f"❌ Failed to save entry with topic: {e}")

def find_match(user_number, topic):
    try:
        return database.find_match(user_number, topic)
    except Exception as e:
        print(f"❌ Failed to find match: {e}")
        return None

# ===== FORMAT JOURNAL =====
def format_journal(entries):
    if not entries:
        return "📖 No entries found. Keep writing — your words matter. 💙"

    formatted = "📖 Your Quiet Loop Journal:\n\n"
    for entry in entries:
        timestamp, entry_type, message = entry
        formatted += f"📅 {timestamp}\n {message}\n\n"
    return formatted + "---\nKeep writing. Your words matter. 💙"

# ===== MORNING CHECK-IN =====
def morning_checkin():
    print(f"🌅 Morning check-in at {datetime.datetime.now()}")
    users = database.get_all_users()
    print(f"👥 Users in database: {users}")
    daily_wisdom = random.choice(wisdom)
    for user in users:
        send_whatsapp(user, f"🌅 Rise and shine! Let's go conquer today. 💪\n\n📖 Daily wisdom:\n{daily_wisdom}\n\nWhat's one thing you're grateful for today?")

# ===== EVENING CHECK-IN =====
def evening_checkin():
    print(f"🌙 Evening check-in at {datetime.datetime.now()}")
    users = database.get_all_users()
    print(f"👥 Users in database: {users}")
    evening_wisdom = random.choice(wisdom)
    for user in users:
        send_whatsapp(user, f"🌙 You made it through another day. Proud of you.\n\n📖 Evening reflection:\n{evening_wisdom}\n\nHow did today go? Reply 'yes' or 'no'.")

# ===== SCHEDULER =====
scheduler = BackgroundScheduler()
scheduler.add_job(morning_checkin, 'cron', hour=8, minute=0)
scheduler.add_job(evening_checkin, 'cron', hour=20, minute=0)
scheduler.start()
print("✅ Scheduler started! Check-ins are active.")

# ===== FLASK ROUTE =====
@app.route("/bot", methods=["POST"])
def bot():
    incoming_msg = request.values.get("Body", "").strip().lower()
    sender = request.values.get("From", "")
    resp = MessagingResponse()
    msg = resp.message()

    state = database.get_user_state(sender)
    journal_state[sender] = journal_state.get(sender, "menu")

    # ===== JOURNAL COMMAND =====
    if incoming_msg == "journal" and state != "journal":
        msg.body("📖 Quiet Loop Journal\n\nWhat would you like to see?\n1. Today's entries\n2. This week's entries\n3. All entries\n4. By date (e.g., 25 June 2026)\n\nReply with 1, 2, 3, or 4.")
        database.save_user_state(sender, "journal")
        journal_state[sender] = "menu"
        return str(resp)

    if state == "journal":
        if journal_state[sender] == "menu":
            if incoming_msg == "1":
                entries = database.get_entries(sender, days=0)
                msg.body(format_journal(entries))
                database.save_user_state(sender, "start")
                journal_state[sender] = "menu"
            elif incoming_msg == "2":
                entries = database.get_entries(sender, days=7)
                msg.body(format_journal(entries))
                database.save_user_state(sender, "start")
                journal_state[sender] = "menu"
            elif incoming_msg == "3":
                entries = database.get_entries(sender)
                msg.body(format_journal(entries))
                database.save_user_state(sender, "start")
                journal_state[sender] = "menu"
            elif incoming_msg == "4":
                msg.body("📅 Please enter the date (e.g., 25 June 2026):")
                journal_state[sender] = "date"
            else:
                msg.body("Please reply with 1, 2, 3, or 4.")
                return str(resp)
        elif journal_state[sender] == "date":
            try:
                date_obj = datetime.datetime.strptime(incoming_msg, "%d %B %Y")
                formatted_date = date_obj.strftime("%Y-%m-%d")
                entries = database.get_entries(sender, specific_date=formatted_date)
                msg.body(format_journal(entries))
            except ValueError:
                msg.body("❌ Invalid date. Please use: 25 June 2026")
                return str(resp)
            database.save_user_state(sender, "start")
            journal_state[sender] = "menu"
        return str(resp)

    # ===== MAIN CONVERSATION =====
    if state == "start":
        if "join" in incoming_msg:
            msg.body("Welcome to Quiet Loop. No calls. No video. Just words.\n\nReply:\n1. Start conversation\n2. Not today")
            database.save_user_state(sender, "menu")
        else:
            msg.body("Reply with 'join' to start.")

    elif state == "menu":
        if incoming_msg == "1":
            msg.body("How has life been treating you lately? Be honest — this is a safe space.")
            database.save_user_state(sender, "life_question")
        elif incoming_msg == "2":
            msg.body("I understand. I'll be here when you're ready. Take care.")
            database.save_user_state(sender, "start")
        else:
            msg.body("Reply:\n1. Start conversation\n2. Not today")

    elif state == "life_question":
        user_reply_store[sender] = incoming_msg
        save_journal_entry(sender, "life_checkin", incoming_msg)
        msg.body("Did you achieve what you set out to do today? Reply 'yes' or 'no'.")
        database.save_user_state(sender, "goal_question")

    elif state == "goal_question":
        if "yes" in incoming_msg:
            save_journal_entry(sender, "goal_achievement", incoming_msg)
            msg.body("🎉 Congratulations! You showed up and you did it. That takes strength. Be proud.")
        elif "no" in incoming_msg:
            save_journal_entry(sender, "goal_achievement", incoming_msg)
            msg.body("It's okay. You tried, and that still counts. Tomorrow is a new chance.")
        else:
            msg.body("Please reply 'yes' or 'no'.")
            return str(resp)

        advice = random.choice(wisdom)
        msg.body(f"{advice}\n\nWant to share your words anonymously?\n1. Yes\n2. No")
        database.save_user_state(sender, "share_question")

    elif state == "share_question":
        if incoming_msg == "1":
            user_reply = user_reply_store.get(sender, "")
            topic = matcher.detect_topic(user_reply)
            save_entry_with_topic(sender, "shared_anonymously", user_reply, topic)

            match = find_match(sender, topic)
            if match:
                match_user, match_message = match
                msg.body(f"💙 Someone else felt this too.\n\n\"{match_message}\"\n\nYou're not alone. Would you like to connect with this person anonymously?\nReply 1 for Yes, 2 for No.")
                database.save_user_state(sender, "match_offer")
            else:
                msg.body("Your words matter. They'll reach someone who needs them today. Stay strong. 💙")
                database.save_user_state(sender, "start")
        elif incoming_msg == "2":
            save_journal_entry(sender, "shared_anonymously", incoming_msg)
            msg.body("I understand. Your words are safe with me. Take care. 💙")
            database.save_user_state(sender, "start")
        else:
            msg.body("Reply 1 for Yes, 2 for No.")
            return str(resp)

    elif state == "match_offer":
        if incoming_msg == "1":
            msg.body("💙 We'll connect you anonymously. Your phone number stays private. Just be kind. 💙")
            database.save_user_state(sender, "start")
        elif incoming_msg == "2":
            msg.body("I understand. Maybe another time. 💙")
            database.save_user_state(sender, "start")
        else:
            msg.body("Reply 1 for Yes, 2 for No.")
            return str(resp)

    else:
        msg.body("Reply with 'join' to start.")
        database.save_user_state(sender, "start")

    return str(resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=True)

