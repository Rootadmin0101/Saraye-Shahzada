import os
import time
import requests
import telebot
from bs4 import BeautifulSoup
from threading import Thread

TOKEN = os.getenv("BOT_TOKEN")  # توکن از Railway
bot = telebot.TeleBot(TOKEN)

# لیست کاربرا
users = set()

# گرفتن نرخ ارز از سایت بانک افغانستان
def get_prices():
    url = "https://www.dab.gov.af/dr/exchange-rates"
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table")
    if not table:
        return "⚠️ جدول نرخ‌ها پیدا نشد."

    rows = table.find_all("tr")
    result = "💱 نرخ امروز:\n\n"
    for row in rows[1:]:
        cols = row.find_all("td")
        if len(cols) >= 3:
            currency = cols[0].get_text(strip=True)
            buy = cols[1].get_text(strip=True)
            sell = cols[2].get_text(strip=True)
            result += f"{currency}: خرید {buy} | فروش {sell}\n"
    return result

# وقتی کاربر استارت بزنه
@bot.message_handler(commands=['start'])
def start(message):
    users.add(message.chat.id)
    bot.reply_to(message, "سلام 👋 از این به بعد نرخ‌ها رو هر ۵ دقیقه برات می‌فرستم ⏳")

# حلقه ارسال خودکار
def send_prices():
    while True:
        if users:
            prices = get_prices()
            for user in list(users):
                try:
                    bot.send_message(user, prices)
                except Exception as e:
                    print(f"خطا در ارسال به {user}: {e}")
        time.sleep(300)  # هر ۵ دقیقه

# اجرای بات
Thread(target=send_prices, daemon=True).start()
bot.infinity_polling()
