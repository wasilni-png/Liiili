import os
import asyncio
import random
from flask import Flask
from threading import Thread
from telethon import TelegramClient

# --- إعدادات Flask لإرضاء Render ---
app = Flask('')

@app.route('/')
def home():
    return "البوت يعمل بنجاح!"

def run_flask():
    # ريندر يرسل رقم المنفذ في متغير PORT
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- إعدادات التليجرام ---
# يفضل وضعها في Environment Variables على ريندر
api_id = 33888256  # استبدله بـ ID الخاص بك
api_hash = 'bb1902689a7e203a7aedadb806c08854' # استبدله بـ Hash الخاص بك

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
<code>0566187430</code>
"""

client = TelegramClient('session_name', api_id, api_hash)

async def send_ads():
    await client.start()
    print("✅ تم تشغيل اليوزربوت...")
    
    while True:
        # جلب المجموعات في كل دورة لتحديث القائمة
        groups = []
        async for dialog in client.iter_dialogs():
            if dialog.is_group:
                groups.append(dialog)
        
        print(f"📊 بدء دورة جديدة على {len(groups)} مجموعة.")
        
        for i in range(0, len(groups), 2):
            batch = groups[i:i+2]
            for group in batch:
                try:
                    await client.send_message(group, ad_message, parse_mode='html')
                    print(f"✅ أرسل إلى: {group.title}")
                except Exception as e:
                    print(f"❌ خطأ في {group.title}: {e}")
            
            wait_time = random.randint(60, 120)
            print(f"⏳ انتظار {wait_time} ثانية...")
            await asyncio.sleep(wait_time)

def start_bot_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(send_ads())

if __name__ == "__main__":
    # تشغيل Flask في خيط منفصل (Thread)
    t = Thread(target=run_flask)
    t.start()
    
    # تشغيل بوت التليجرام
    start_bot_loop()
