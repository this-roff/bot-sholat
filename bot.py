from telegram.ext import Application
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz
import requests
from datetime import datetime

BOT_TOKEN = "8895745270:AAFuPDQP2H6xnq-cJXQ2Ji57UzxOPEKR538"
CHAT_ID = "6931190446"

KOTA = "Medan"
NEGARA = "Indonesia"
TIMEZONE = pytz.timezone("Asia/Jakarta")

app = Application.builder().token(BOT_TOKEN).build()

def ambil_jadwal_sholat():
    url = "http://api.aladhan.com/v1/timingsByCity"
    params = {"city": KOTA, "country": NEGARA, "method": 11}
    res = requests.get(url, params=params).json()
    t = res["data"]["timings"]
    return {
        "Subuh": t["Fajr"],
        "Dzuhur": t["Dhuhr"],
        "Ashar": t["Asr"],
        "Maghrib": t["Maghrib"],
        "Isya": t["Isha"],
    }

async def send_reminder(nama_sholat, jam):
    pesan = (
        f"🕌 *WAKTU SHOLAT TIBA*\n\n"
        f"✨ *{nama_sholat}*\n"
        f"⏰ Pukul {jam} WIB\n"
        f"📍 {KOTA}\n\n"
        f"_Yuk sholat, jangan ditunda!_ 🤲"
    )
    await app.bot.send_message(chat_id=CHAT_ID, text=pesan, parse_mode="Markdown")

def jadwalkan_hari_ini(scheduler):
    jadwal = ambil_jadwal_sholat()
    for nama, jam in jadwal.items():
        jam_int, menit_int = map(int, jam.split(":"))
        scheduler.add_job(
            send_reminder,
            'cron',
            hour=jam_int,
            minute=menit_int,
            args=[nama, jam],
            id=nama,
            replace_existing=True
        )
    print(f"Jadwal hari ini ({datetime.now().date()}):", jadwal)

def main():
    scheduler = AsyncIOScheduler(timezone=TIMEZONE)
    jadwalkan_hari_ini(scheduler)
    scheduler.add_job(jadwalkan_hari_ini, 'cron', hour=0, minute=5, args=[scheduler])
    scheduler.start()
    print("Bot aktif, reminder sholat terjadwal!")
    app.run_polling()

if __name__ == "__main__":
    main()
