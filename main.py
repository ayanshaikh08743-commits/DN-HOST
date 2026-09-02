import os
import telebot
import random
import time
import threading
from flask import Flask
from supabase import create_client, Client

# --- 1. FLASK WEB SERVER FOR RENDER PORT BINDING ---
app = Flask('')

@app.route('/')
def health_check():
    return "✅ DN-HOST Bot Status: HEALTHY 24/7"

def run_web_server():
    # Render PORT environment variable padhta hai
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- 2. CONFIG ---
TOKEN = "8979677830:AAHkQj3nbESPko8TMVEVLXnoFCMHgc2RWwY"
URL = "https://kytsbcazzsgpoaudzvwc.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt5dHNiY2F6enNncG9hdWR6dndjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODM5NTY2MTksImV4cCI6MjA5OTUzMjYxOX0.ZNIegUWXY9vLUIGCHO8Ww-cv8UJdsvBePS8ssaQewnQ"

bot = telebot.TeleBot(TOKEN)
supabase: Client = create_client(URL, KEY)
user_data = {}

# Clear webhooks on startup to prevent 409 conflicts
try:
    bot.remove_webhook()
    print("✅ Webhooks cleared successfully!")
except Exception as e:
    print(f"Webhook warning: {e}")

print("🚀 DNPAY RENDER CLOUD BOT SERVER STARTING...")

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
            try:
                supabase.table("profiles").update({"is_bot_active": True, "security_pin": text, "phone": state["phone"]}).eq("invite_code", state["uid"]).execute()
                bot.send_message(cid, f"💎 *SECURITY ACTIVE!*\n\nPIN: *{text}*\n\nAb app mein wallets link kar sakte hain.", parse_mode="Markdown")
                del user_data[cid]
            except Exception as e:
                bot.send_message(cid, "❌ Database Error!")
        else:
            bot.send_message(cid, "⚠️ Sirf 4 digits PIN likhein.")

if __name__ == "__main__":
    # Start Web Server on PORT in background thread for Render
    threading.Thread(target=run_web_server, daemon=True).start()
    
    # Run Bot Polling with retry loop
    while True:
        try:
            bot.polling(none_stop=True, interval=2, timeout=40)
        except Exception as e:
            print(f"Polling retry: {e}")
            time.sleep(5)
