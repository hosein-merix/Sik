import asyncio
import sqlite3
import random
import requests
from datetime import datetime, date
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

# --- توکن ربات ---
BOT_TOKEN = "8228537965:AAFBwx_exehFblFTqQ9apfRMN_aYtFZYMVs"  # اینجا توکن جدیدت رو بذار

# --- تنظیمات ---
FISHER_ID = "@Nonobodyno666"

# --- دیتابیس SQLite ---
conn = sqlite3.connect("fisherbot.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    score_total INTEGER DEFAULT 0,
    last_rate TEXT
)
""")
conn.commit()

# --- بات ---
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- کیبورد اصلی ---
main_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🎀 ارتباط با فیشر", url=f"https://t.me/{FISHER_ID[1:]}")],
    [InlineKeyboardButton(text="📥 دانلود اینستا", callback_data="dl")],
    [InlineKeyboardButton(text="⭐ امتیاز کیوتی", callback_data="rate")],
    [InlineKeyboardButton(text="🏆 لیست گلب‌ترین‌ها", callback_data="top")]
])

# --- استارت ---
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        f"سلام {message.from_user.first_name} ناناز~ ✨\n"
        f"من ربات اختصاصی {FISHER_ID} هستم 🌸\n"
        "یکی از گزینه‌های زیر رو انتخاب کن:",
        reply_markup=main_kb
    )

# --- دانلود اینستا ---
@dp.callback_query(lambda c: c.data == "dl")
async def ask_dl(callback: types.CallbackQuery):
    await callback.message.answer("📥 لینک اینستاگرام رو برام بفرست (پست یا ریل عمومی).")

@dp.message()
async def insta_dl(message: types.Message):
    if "instagram.com" in message.text:
        try:
            # استفاده از API آماده (نمونه)
            api_url = f"https://api.ryzendesu.vip/instadl?url={message.text}"
            r = requests.get(api_url).json()
            if r.get("success") and "media" in r:
                for link in r["media"]:
                    await message.answer_video(link)
            else:
                await message.answer("❌ نتونستم دانلود کنم (لینک پابلیک بده).")
        except:
            await message.answer("⚠️ خطا در دانلود.")
    else:
        return  # پیام معمولی

# --- امتیاز روزانه ---
@dp.callback_query(lambda c: c.data == "rate")
async def rate(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username or callback.from_user.first_name
    today = str(date.today())

    cursor.execute("SELECT score_total, last_rate FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()

    if row:
        score_total, last_rate = row
        if last_rate == today:
            await callback.message.answer("⭐ تو امروز قبلاً امتیاز گرفتی، فردا دوباره بیا! 🌸")
            return
    else:
        cursor.execute("INSERT INTO users (user_id, username, score_total, last_rate) VALUES (?, ?, ?, ?)",
                       (user_id, username, 0, today))
        conn.commit()
        score_total, last_rate = 0, None

    score = random.randint(1, 100)
    new_total = score_total + score
    cursor.execute("UPDATE users SET score_total=?, last_rate=? WHERE user_id=?",
                   (new_total, today, user_id))
    conn.commit()

    await callback.message.answer(f"⭐ امروز امتیاز کیوتی تو {score}/100 شد! 🌸\n"
                                  f"🔮 مجموع امتیازاتت: {new_total}")

# --- لیست گلب‌ترین‌ها ---
@dp.callback_query(lambda c: c.data == "top")
async def top_list(callback: types.CallbackQuery):
    cursor.execute("SELECT username, score_total FROM users ORDER BY score_total DESC LIMIT 10")
    rows = cursor.fetchall()
    if not rows:
        await callback.message.answer("🏆 هنوز کسی امتیاز نگرفته!")
        return
    text = "🏆 لیست گلب‌ترین‌های فیشر 🏆\n\n"
    for i, (username, score) in enumerate(rows, start=1):
        user_disp = f"@{username}" if username else "کاربر ناشناس"
        text += f"{i}. {user_disp} — {score} امتیاز\n"
    await callback.message.answer(text)

# --- ران ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
