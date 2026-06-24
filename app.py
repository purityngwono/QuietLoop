from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from apscheduler.schedulers.background import BackgroundScheduler
import random
import datetime
import os

app = Flask(__name__)

# ===== TWILIO CREDENTIALS =====
# Get these from Twilio Console → Dashboard
ACCOUNT_SID = "AC564a593b6421d0146c76daa" # Replace with yours
AUTH_TOKEN = "5e4087a6660c392f29582fdd93a4ad69" # Replace with yours
FROM_NUMBER = "whatsapp:+14155238886"

twilio_client = Client(ACCOUNT_SID, AUTH_TOKEN)

# ===== ADVICE LIST =====
advice_list = [
    "You don't have to be perfect to be worthy. Just showing up is enough.",
    "Rest is not laziness. It's repair. Take the break you deserve.",
    "Nobody remembers your mistakes as much as you do. Forgive yourself.",
    "Small steps still move you forward. Keep going, even if it's slow.",
    "You are not what happened to you. You are what you choose to become.",
    "Your value doesn't decrease when your energy does. You're still enough.",
    "The quiet ones often have the loudest wisdom. Trust your voice.",
    "You don't need permission to exist exactly as you are right now.",
    "Sometimes healing looks like doing nothing. That's okay.",
    "Your goal today was enough. Tomorrow is another chance."
]

# ===== USER DATA =====
user_state = {}
user_name = {} # Store user's name if they share it

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
    for user in user_state.keys():
        send_whatsapp(user, "🌅 Rise and shine! Wake up - let's go conquer today. You've got this. \n\nWhat's one thing you're grateful for today?")

# ===== EVENING CHECK-IN =====
def evening_checkin():
    print(f"🌙 Evening check-in at {datetime.datetime.now()}")
    for user in user_state.keys():
        send_whatsapp(user, "🌙 You made it through another day. Proud of you.\n\nHow did today go? Did you achieve what you wanted to? Reply 'yes' or 'no'.")

# ===== SCHEDULER =====
scheduler = BackgroundScheduler()
scheduler.add_job(morning_checkin, 'cron', hour=8, minute=0) # 8:00 AM
scheduler.add_job(evening_checkin, 'cron', hour=20, minute=0) # 8:00 PM
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
        
        advice = random.choice(advice_list)
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
