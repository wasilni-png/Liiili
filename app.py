import os
import asyncio
import random
from flask import Flask
from threading import Thread
from telethon import TelegramClient

# --- إعدادات Flask لإبقاء السيرفر مستيقظاً ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is Running!"

def run_flask():
    # ريندر يستخدم المنفذ 10000 تلقائياً أو PORT المحجوز
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- إعدادات التليجرام ---
api_id = 33888256  # ضع رقمك هنا
api_hash = 'bb1902689a7e203a7aedadb806c08854' # ضع الهاش هنا

ad_message = """
<b>🌟 التميز والاحترافية لخدمتكم 🌟</b>

<b>✅ خدمات النقل:</b>
• توفير سائقين بالشهر (للمشاوير الجامعية والدوامات) 🚗

<b>✅ الخدمات الأكاديمية والتعليمية:</b>
• حل جميع الواجبات والبحوثات العلمية 📚
• إعداد الأطروحات وملفات الأداء الوظيفي للمعلمات 👩‍🏫

<b>✅ التوظيف والمهنة:</b>
• تصميم سيرة ذاتية احترافية بنظام <b>ATS</b> العالمي 📄
<i>(لضمان قبولك في أنظمة الفرز الآلي للشركات)</i>

──────────────────
📞 <b>للتواصل والاستفسار (اتصال أو واتساب):</b>
<code>+0566187430</code>
"""

# ملاحظة: أضفنا receive_updates=False لحل مشكلة Constructor ID نهائياً
client = TelegramClient('session_name', api_id, api_hash, receive_updates=False)

async def send_ads():
    print("⏳ جاري محاولة الاتصال بتيليجرام...")
    await client.start()
    me = await client.get_me()
    print(f"✅ تم تسجيل الدخول باسم: {me.first_name}")
    
    while True:
        try:
            # جلب المجموعات
            groups = []
            async for dialog in client.iter_dialogs():
                if dialog.is_group:
                    groups.append(dialog)
            
            print(f"📊 تم العثور على {len(groups)} مجموعة. بدء الإرسال...")
            
            for i in range(0, len(groups), 2):
                batch = groups[i:i+2]
                for group in batch:
                    try:
                        await client.send_message(group, ad_message, parse_mode='html')
                        print(f"✔️ تم الإرسال إلى: {group.title}")
                    except Exception as e:
                        print(f"⚠️ فشل الإرسال لـ {group.title}: {e}")
                
                # الانتظار بين دقيقة ودقيقتين
                wait_time = random.randint(60, 120)
                print(f"⏳ انتظار {wait_time} ثانية قبل الدفعة التالية...")
                await asyncio.sleep(wait_time)
            
            print("🔁 انتهت الدورة. الانتظار 5 دقائق قبل البدء من جديد...")
            await asyncio.sleep(300) 

        except Exception as e:
            print(f"❌ خطأ غير متوقع في الحلقة الرئيسية: {e}")
            await asyncio.sleep(30) # انتظار بسيط قبل إعادة المحاولة

def start_bot_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(send_ads())

if __name__ == "__main__":
    # تشغيل Flask في خيط مستقل
    t = Thread(target=run_flask)
    t.daemon = True # لضمان إغلاق الخيط عند توقف البرنامج
    t.start()
    
    # تشغيل دورة البوت
    start_bot_loop()
