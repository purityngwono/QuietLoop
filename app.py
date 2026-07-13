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
ACCOUNT_SID = "your_account_sid_here"
AUTH_TOKEN = "your_auth_token_here"
FROM_NUMBER = "whatsapp:+14155238886"

twilio_client = Client(ACCOUNT_SID, AUTH_TOKEN)

# ===== WISDOM LIBRARY (Poetic + NF-inspired) =====
wisdom = [
    "You showed up. Even if you didn't finish. Even if it was hard. That's not failure. That's surviving.",
    "The night is long, but you're still standing. That counts for more than you know.",
    "You didn't give up. You're still breathing. That's a victory.",
    "It's not about being perfect. It's about being present. And you are.",
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

# ===== POETIC RESPONSES =====
poetic = {
    "acknowledgment": [
        "That sounds really heavy. Thank you for trusting this space with it.",
        "I hear you. That's not easy to say. Thank you for saying it here.",
        "That weight you're carrying — I see it. Thank you for letting me hold it for a moment.",
        "That's a lot to carry. I'm glad you shared it here.",
    ],
    "farewell": [
        "The day is done. The night is for resting. Be gentle with yourself.",
        "You made it through today. That's enough. Sleep well.",
        "The sun is setting, and so are the worries of today. Let them go.",
        "Rest now. Tomorrow is a new page.",
    ]
}

# ===== CRISIS RESPONSE (Global) =====
crisis_response = """I'm just a bot, but your life matters. ❤️

Here are some humans who can help — available 24/7, anywhere in the world:

🌍 **Global** (International)
• Befrienders Worldwide: https://befrienders.org
• International Association for Suicide Prevention: https://iasp.info

🇺🇸 **USA**: 988 Suicide & Crisis Lifeline — call or text 988
🇬🇧 **UK**: Samaritans — call 116 123
🇰🇪 **Kenya**: Befrienders Kenya — call +254 722 178 177
🇿🇦 **South Africa**: SADAG — call 0800 567 567
🇮🇳 **India**: iCall — call 022 2556 3291

You're not alone. Please reach out to someone who can hold this with you. 💙"""

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
    saved = database.save_entry(user_number, entry_type, message)
    if saved:
        print(f"📖 Saved journal entry for {user_number}")
    else:
        print(f"⏭️ Skipped duplicate entry for {user_number}")
    return saved

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

# ===== EVENING WIND-DOWN (9 PM) =====
def evening_wind_down():
    print(f"🌙 Evening wind-down at {datetime.datetime.now()}")
    users = database.get_all_users()
    farewell = random.choice(poetic["farewell"])
    for user in users:
        send_whatsapp(user, f"🌙 {farewell}")

# ===== SCHEDULER =====
scheduler = BackgroundScheduler()
scheduler.add_job(morning_checkin, 'cron', hour=8, minute=0)
scheduler.add_job(evening_checkin, 'cron', hour=20, minute=0)
scheduler.add_job(evening_wind_down, 'cron', hour=21, minute=0) # 9:00 PM
scheduler.start()
print("✅ Scheduler started! Check-ins are active.")

# ===== FLASK ROUTE =====
@app.route("/bot", methods=["POST"])
def bot():
    incoming_msg = request.values.get("Body", "").strip()
    sender = request.values.get("From", "")
    resp = MessagingResponse()
    msg = resp.message()

    # ===== NORMALIZE MESSAGE (emoji + slang) =====
    clean_msg = matcher.normalize_message(incoming_msg)
    print(f"📩 Raw: {incoming_msg}")
    print(f"🧹 Clean: {clean_msg}")
    print(f"🚨 Crisis check: {matcher.is_crisis(clean_msg)}")
    print(f"📖 Journal check: {clean_msg == 'journal'}")

    # ===== CRISIS CHECK (FIRST) =====
    if matcher.is_crisis(clean_msg):
        msg.body(crisis_response)
        return str(resp)

    state = database.get_user_state(sender)
    journal_state[sender] = journal_state.get(sender, "menu")

    # ===== JOURNAL COMMAND =====
    if clean_msg == "journal" and state != "journal":
        msg.body("📖 Quiet Loop Journal\n\nWhat would you like to see?\n1. Today's entries\n2. This week's entries\n3. All entries\n4. By date (e.g., 25 June 2026)\n\nReply with 1, 2, 3, or 4.")
        database.save_user_state(sender, "journal")
        journal_state[sender] = "menu"
        return str(resp)

    if state == "journal":
        if journal_state[sender] == "menu":
            if clean_msg == "1":
                entries = database.get_entries(sender, days=0)
                msg.body(format_journal(entries))
                database.save_user_state(sender, "start")
                journal_state[sender] = "menu"
            elif clean_msg == "2":
                entries = database.get_entries(sender, days=7)
                msg.body(format_journal(entries))
                database.save_user_state(sender, "start")
                journal_state[sender] = "menu"
            elif clean_msg == "3":
                entries = database.get_entries(sender)
                msg.body(format_journal(entries))
                database.save_user_state(sender, "start")
                journal_state[sender] = "menu"
            elif clean_msg == "4":
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

    # ===== REPLY TO MATCH =====
    if clean_msg.startswith("reply"):
        match_data = database.get_match(sender)
        if match_data:
            match_id, matched_user, their_message = match_data
            if clean_msg == "reply":
                msg.body(f"💙 Reply to: \"{their_message}\"\n\nType your message below.")
                database.save_user_state(sender, "reply_to_match")
                return str(resp)
            else:
                # User sent: "reply This is my message"
                reply_text = incoming_msg[6:].strip()
                if reply_text:
                    database.save_reply(match_id, reply_text)
                    send_whatsapp(matched_user, f"💙 Someone you matched with sent you a quiet reply:\n\n\"{reply_text}\"")
                    msg.body("✅ Your reply was sent anonymously. 💙")
                    database.save_user_state(sender, "start")
                else:
                    msg.body("Please type a message after 'reply'.")
                return str(resp)
        else:
            msg.body("You don't have an active match to reply to.")
            database.save_user_state(sender, "start")
            return str(resp)

    # ===== MAIN CONVERSATION =====
    if state == "start":
        if "join" in clean_msg:
            # Check if returning user
            mood = database.get_mood(sender)
            if mood:
                welcome = f"Welcome back. Last time you said life felt {mood}. How is today?"
            else:
                welcome = "Welcome to Quiet Loop. No calls. No video. Just words."
            
            msg.body(f"{welcome}\n\nReply:\n1. Start conversation\n2. Not today")
            database.save_user_state(sender, "menu")
        else:
            msg.body("Reply with 'join' to start.")

    elif state == "menu":
        if clean_msg == "1":
            msg.body("How has life been treating you lately? Be honest — this is a safe space.")
            database.save_user_state(sender, "life_question")
        elif clean_msg == "2":
            farewell = random.choice(poetic["farewell"])
            msg.body(f"{farewell}")
            database.save_user_state(sender, "start")
        else:
            msg.body("Reply:\n1. Start conversation\n2. Not today")

    elif state == "life_question":
        user_reply_store[sender] = incoming_msg
        save_journal_entry(sender, "life_checkin", incoming_msg)
        
        # Save mood for returning greeting
        mood = matcher.extract_mood(clean_msg)
        database.save_mood(sender, mood)
        
        # Heavy message acknowledgment
        if matcher.is_heavy_message(clean_msg):
            ack = random.choice(poetic["acknowledgment"])
            msg.body(f"{ack}\n\nDid you achieve what you set out to do today? Reply 'yes' or 'no'.")
            database.save_user_state(sender, "goal_question")
        else:
            msg.body("Did you achieve what you set out to do today? Reply 'yes' or 'no'.")
            database.save_user_state(sender, "goal_question")

    elif state == "goal_question":
        if "yes" in clean_msg:
            save_journal_entry(sender, "goal_achievement", incoming_msg)
            msg.body("🎉 That's beautiful. You showed up and you did it. That takes strength. Be proud.")
        elif "no" in clean_msg:
            save_journal_entry(sender, "goal_achievement", incoming_msg)
            msg.body("It's okay. You tried, and that still counts. Tomorrow is a new chance.")
        else:
            msg.body("Please reply 'yes' or 'no'.")
            return str(resp)

        advice = random.choice(wisdom)
        msg.body(f"{advice}\n\nWant to share your words anonymously?\n1. Yes\n2. No\n3. Send a quiet reply")
        database.save_user_state(sender, "share_question")

    elif state == "share_question":
        if clean_msg == "1":
            user_reply = user_reply_store.get(sender, "")
            topic = matcher.detect_topic(clean_msg)
            save_entry_with_topic(sender, "shared_anonymously", user_reply, topic)

            match = find_match(sender, topic)
            if match:
                matched_user, match_message = match
                msg.body(f"💙 Someone else felt this too.\n\n\"{match_message}\"\n\nYou're not alone. Would you like to connect with this person anonymously?\n1. Yes\n2. No\n3. Send a quiet reply")
                database.save_user_state(sender, "match_offer")
                # Store match info for later
                user_reply_store[sender + "_match_user"] = matched_user
                user_reply_store[sender + "_match_message"] = match_message
            else:
                msg.body("Your words matter. They'll reach someone who needs them today. Stay strong. 💙")
                database.save_user_state(sender, "start")
        elif clean_msg == "2":
            save_journal_entry(sender, "shared_anonymously", incoming_msg)
            msg.body("I understand. Your words are safe with me. Take care. 💙")
            database.save_user_state(sender, "start")
        elif clean_msg == "3":
            match_data = database.get_match(sender)
            if match_data:
                match_id, matched_user, their_message = match_data
                msg.body(f"💙 Reply to: \"{their_message}\"\n\nType your message below.")
                database.save_user_state(sender, "reply_to_match")
            else:
                msg.body("You don't have an active match to reply to.")
                database.save_user_state(sender, "start")
        else:
            msg.body("Reply 1 for Yes, 2 for No, or 3 for quiet reply.")
            return str(resp)

    elif state == "match_offer":
        if clean_msg == "1":
            matched_user = user_reply_store.get(sender + "_match_user")
            match_message = user_reply_store.get(sender + "_match_message")
            if matched_user and match_message:
                database.save_match_sent(sender, matched_user, match_message)
                msg.body("💙 We'll connect you anonymously. Your phone number stays private. Just be kind. 💙\n\nYou can send a quiet reply anytime by typing 'reply'.")
                database.save_user_state(sender, "start")
            else:
                msg.body("Something went wrong. Please try sharing again.")
                database.save_user_state(sender, "start")
        elif clean_msg == "2":
            msg.body("I understand. Maybe another time. 💙")
            database.save_user_state(sender, "start")
        elif clean_msg == "3":
            match_data = database.get_match(sender)
            if match_data:
                match_id, matched_user, their_message = match_data
                msg.body(f"💙 Reply to: \"{their_message}\"\n\nType your message below.")
                database.save_user_state(sender, "reply_to_match")
            else:
                msg.body("You don't have an active match to reply to.")
                database.save_user_state(sender, "start")
        else:
            msg.body("Reply 1 for Yes, 2 for No, or 3 for quiet reply.")
            return str(resp)

    elif state == "reply_to_match":
        match_data = database.get_match(sender)
        if match_data:
            match_id, matched_user, their_message = match_data
            database.save_reply(match_id, incoming_msg)
            send_whatsapp(matched_user, f"💙 Someone you matched with sent you a quiet reply:\n\n\"{incoming_msg}\"")
            msg.body("✅ Your reply was sent anonymously. 💙")
            database.save_user_state(sender, "start")
        else:
            msg.body("No active match found.")
            database.save_user_state(sender, "start")

    else:
        msg.body("Reply with 'join' to start.")
        database.save_user_state(sender, "start")

    return str(resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=True)

