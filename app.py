from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from apscheduler.schedulers.background import BackgroundScheduler
import random
import datetime
import os

app = Flask(__name__)

# ===== WAKE ROUTE FOR CRON-JOB =====
@app.route("/", methods=["GET"])
def wake():
    return "Quiet Loop is awake! 💙", 200

# ===== TWILIO CREDENTIALS =====
ACCOUNT_SID = "AC564a593b6421d0146c76daa" # Replace with yours
AUTH_TOKEN = "5e4087a6660c392f29582fd9d93a4ad69" # Replace with yours
FROM_NUMBER = "whatsapp:+14155238886"

twilio_client = Client(ACCOUNT_SID, AUTH_TOKEN)

# ===== WISDOM LIBRARY (NF + Classics) =====
wisdom = [
    # NF-inspired
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
    
    # Classic wisdom
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
user_state = {}

# ===== SEND MESSAGE FUNCTION =====
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

# ===== MORNING CHECK-IN =====
def morning_checkin():
    print(f"🌅 Morning check-in at {datetime.datetime.now()}")
    daily_wisdom = random.choice(wisdom)
    for user in user_state.keys():
        send_whatsapp(
            user,
            f"🌅 Rise and shine! Wake up — let's go conquer today. You've got this. 💪\n\n📖 Daily wisdom:\n{daily_wisdom}\n\nWhat's one thing you're grateful for today?"
        )

# ===== EVENING CHECK-IN =====
def evening_checkin():
    print(f"🌙 Evening check-in at {datetime.datetime.now()}")
    evening_wisdom = random.choice(wisdom)
    for user in user_state.keys():
        send_whatsapp(
            user,
            f"🌙 You made it through another day. Proud of you.\n\n📖 Evening reflection:\n{evening_wisdom}\n\nHow did today go? Did you achieve what you wanted to? Reply 'yes' or 'no'."
        )

# ===== SCHEDULER =====
scheduler = BackgroundScheduler()
scheduler.add_job(morning_checkin, 'cron', hour=8, minute=0)
scheduler.add_job(evening_checkin, 'cron', hour=20, minute=0)
scheduler.start()

# ===== FLASK ROUTE =====
@app.route("/bot", methods=["POST"])
def bot():
    incoming_msg = request.values.get("Body", "").strip().lower()
    sender = request.values.get("From", "")
    resp = MessagingResponse()
    msg = resp.message()

    state = user_state.get(sender, "start")

    if state == "start":
        if "join" in incoming_msg:
            msg.body("Welcome to Quiet Loop. No calls. No video. Just words.\n\nReply:\n1. Start conversation\n2. Not today")
            user_state[sender] = "menu"
        else:
            msg.body("Reply with 'join' to start your quiet conversation.")
    
    elif state == "menu":
        if incoming_msg == "1":
            msg.body("How has life been treating you lately? Be honest — this is a safe space.")
            user_state[sender] = "life_question"
        elif incoming_msg == "2":
            msg.body("I understand. I'll be here when you're ready. Take care of yourself.")
            user_state[sender] = "start"
        else:
            msg.body("Reply:\n1. Start conversation\n2. Not today")
    
    elif state == "life_question":
        msg.body("Did you achieve what you set out to do today? Reply 'yes' or 'no'.")
        user_state[sender] = "goal_question"
    
    elif state == "goal_question":
        if "yes" in incoming_msg:
            msg.body("🎉 Congratulations! You showed up and you did it. That takes strength. Be proud of yourself.")
        elif "no" in incoming_msg:
            msg.body("It's okay. You tried, and that still counts. Tomorrow is a new chance. Don't give up.")
        else:
            msg.body("Please reply 'yes' or 'no'.")
            return str(resp)
        
        advice = random.choice(wisdom) # Uses wisdom list instead of old advice list
        msg.body(f"{advice}\n\nWant me to share your words anonymously with someone who might need them?\n1. Yes\n2. No")
        user_state[sender] = "share_question"
    
    elif state == "share_question":
        if incoming_msg == "1":
            msg.body("Your words matter. They'll reach someone who needs them today. Stay strong. 💙")
        elif incoming_msg == "2":
            msg.body("I understand. Your words are safe with me. Take care of yourself. 💙")
        else:
            msg.body("Reply 1 for Yes, 2 for No.")
            return str(resp)
        user_state[sender] = "start"
    
    else:
        msg.body("Reply with 'join' to start your quiet conversation.")
        user_state[sender] = "start"

    return str(resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=True)

