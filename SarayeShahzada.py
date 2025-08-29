import time
import requests
from bs4 import BeautifulSoup
from threading import Thread

TOKEN = "YOUR_BOT_TOKEN"
URL = f"https://api.telegram.org/bot{TOKEN}/"
users = set()  # لیست کاربرانی که /start زده‌اند

def get_rates():
    res = requests.get("https://www.dab.gov.af/dr/exchange-rates")
    soup = BeautifulSoup(res.text, "html.parser")
    rows = soup.select("table tr")
    rates = []
    for row in rows[1:]:  # رد کردن هدر
        cols = row.find_all("td")
        if len(cols) >= 2:
            currency = cols[0].get_text(strip=True)
            price = cols[1].get_text(strip=True)
            rates.append(f"{currency} : {price}")
    return "📊 نرخ ارزهای امروز:\n\n" + "\n".join(rates)

def send_message(chat_id, text):
    requests.post(URL + "sendMessage", json={"chat_id": chat_id, "text": text})

def handle_updates():
    offset = None
    while True:
        resp = requests.get(URL + "getUpdates", params={"offset": offset, "timeout": 20}).json()
        for update in resp.get("result", []):
            offset = update["update_id"] + 1
            if "message" in update and "text" in update["message"]:
                chat_id = update["message"]["chat"]["id"]
                text = update["message"]["text"]
                if text == "/start":
                    users.add(chat_id)
                    send_message(chat_id, "سلام! ✅ از این به بعد نرخ ارزها هر چند دقیقه برایت میاد.")
        time.sleep(1)

def scheduler(interval=300):  # هر 300 ثانیه (5 دقیقه)
    while True:
        rates = get_rates()
        for user in users:
            send_message(user, rates)
        time.sleep(interval)

# اجرای دو thread همزمان: یکی برای گرفتن آپدیت‌ها، یکی برای ارسال زمان‌بندی‌شده
Thread(target=handle_updates).start()
Thread(target=scheduler).start()
