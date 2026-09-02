import os
import telebot
import requests
import random
import time

# --- NEW BOT TOKEN UPDATED ---
TOKEN = "8979677830:AAHkQj3nbESPko8TMVEVLXnoFCMHgc2RWwY"
SUPABASE_URL = "https://kytsbcazzsgpoaudzvwc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt5dHNiY2F6enNncG9hdWR6dndjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODM5NTY2MTksImV4cCI6MjA5OTUzMjYxOX0.ZNIegUWXY9vLUIGCHO8Ww-cv8UJdsvBePS8ssaQewnQ"

bot = telebot.TeleBot(TOKEN)
user_data = {}

try:
    bot.remove_webhook()
    print("✅ Old Webhooks Cleared!")
except: pass

def update_supabase_profile(invite_code, pin, phone):
    url = f"{SUPABASE_URL}/rest/v1/profiles?invite_code=eq.{invite_code}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    payload = {
        "is_bot_active": True,
        "security_pin": pin,
        "phone": phone
    }
    try:
        res = requests.patch(url, json=payload, headers=headers)
        return res.status_code in [200, 204]
    except:
        return False

print("🚀 NEW DNPAY SECURITY BOT IS ONLINE!")

@bot.message_handler(commands=['start'])
def start(message):
    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(message.chat.id, "❌ Kripya app se start karein.")
        return
    
    uid = parts[1]
    user_data[message.chat.id] = {"uid": uid, "step": "PHONE"}
    bot.send_message(message.chat.id, f"🔐 *VIP SECURITY*\n\nUser ID: *{uid}*\n\nApna mobile number likhein:", parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def process_flow(message):
    cid = message.chat.id
    text = message.text.strip()
    if cid not in user_data or text.startswith('/start'): return
    
    state = user_data[cid]

    if state["step"] == "PHONE":
        if text.isdigit() and len(text) == 10:
            otp = str(random.randint(100000, 999999))
            user_data[cid].update({"otp": otp, "step": "OTP", "phone": text})
            bot.send_message(cid, f"🔢 OTP: *{otp}*\n\nType karein:", parse_mode="Markdown")
        else:
            bot.send_message(cid, "⚠️ Sahi 10-digit number likhein.")

    elif state["step"] == "OTP":
        if text == state["otp"]:
            user_data[cid]["step"] = "PIN"
            bot.send_message(cid, "🎯 Verified! Ab 4-Digit Security PIN set karein:")
        else:
            bot.send_message(cid, "❌ Galat OTP!")

    elif state["step"] == "PIN":
        if text.isdigit() and len(text) == 4:
            success = update_supabase_profile(state["uid"], text, state["phone"])
            if success:
                bot.send_message(cid, f"💎 *SECURITY ACTIVE!*\n\nPIN: *{text}*\n\nAb app mein wallets link kar sakte hain.", parse_mode="Markdown")
                del user_data[cid]
            else:
                bot.send_message(cid, "❌ Database Error!")
        else:
            bot.send_message(cid, "⚠️ Sirf 4 digits PIN likhein.")

while True:
    try:
        bot.polling(none_stop=True, interval=0, timeout=50)
    except Exception as e:
        time.sleep(5)
