import os
import asyncio
import random
import glob
from flask import Flask
from threading import Thread
from telethon import TelegramClient

# ==========================================
# 1. إعدادات السيرفر (Flask) لـ Render
# ==========================================
app = Flask('')

@app.route('/')
def home():
    return "✅ System is Running! | Telegram Auto-Sender"

def run_flask():
    # ريندر يرسل المنفذ تلقائياً، أو نستخدم 10000 كبديل
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# ==========================================
# 2. إعدادات التليجرام (الثابتة)
# ==========================================
# يمكنك استخدام نفس الـ API لجميع الحسابات
API_ID = 33888256
API_HASH = 'bb1902689a7e203a7aedadb806c08854'

# نص الإعلان الموحد
AD_MESSAGE = """
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

# ==========================================
# 3. وظيفة عمل البوت (لكل حساب)
# ==========================================
async def run_worker(session_file):
    session_name = os.path.splitext(session_file)[0]
    
    try:
        # التعديل: تعطيل التحديثات تماماً
        client = TelegramClient(session_name, API_ID, API_HASH, receive_updates=False)
        
        print(f"🔌 جاري اتصال الحساب: {session_name}...")
        await client.start()
        
        me = await client.get_me()
        bot_name = me.first_name
        print(f"✅ تم دخول الحساب بنجاح: {bot_name}")

        while True:
            try:
                groups = []
                # تعديل: محاولة جلب المجموعات مع تخطي أخطاء التنسيق (Constructor ID)
                try:
                    async for dialog in client.iter_dialogs(ignore_migrated=True):
                        if dialog.is_group or dialog.is_channel:
                            groups.append(dialog)
                except Exception as e:
                    print(f"⚠️ [{bot_name}] تنبيه أثناء قراءة المجموعات: {e}")
                    # إذا فشل iter_dialogs، سيستمر البرنامج بما وجده أو يحاول لاحقاً
                
                if not groups:
                    print(f"ℹ️ [{bot_name}] لم يتم العثور على مجموعات حالياً.")
                    await asyncio.sleep(100)
                    continue

                print(f"📊 [{bot_name}] وجد {len(groups)} وجهة. جاري الإرسال...")
                
                for i in range(0, len(groups), 2):
                    batch = groups[i:i+2]
                    for group in batch:
                        try:
                            # الإرسال باستخدام ID المجموعة مباشرة لتجنب أخطاء التنسيق
                            await client.send_message(group.id, AD_MESSAGE, parse_mode='html')
                            print(f"🚀 [{bot_name}] تم الإرسال -> {group.title}")
                        except Exception as e:
                            print(f"⚠️ [{bot_name}] تخطي {group.title}: {e}")
                    
                    wait = random.randint(60, 90) # زيادة الوقت قليلاً للأمان
                    print(f"⏳ [{bot_name}] استراحة {wait} ثانية...")
                    await asyncio.sleep(wait)
                
                print(f"🏁 [{bot_name}] أكمل الدورة. خمول لمدة 15 دقيقة...")
                await asyncio.sleep(300)

            except Exception as e:
                print(f"❌ خطأ في دورة [{bot_name}]: {e}")
                await asyncio.sleep(60)

    except Exception as e:
        print(f"🚫 فشل نهائي في جلسة {session_name}: {e}")

# ==========================================
# 4. المشغل الرئيسي (Main)
# ==========================================
async def main():
    # البحث عن كل ملفات .session في المجلد
    session_files = glob.glob("*.session")
    
    if not session_files:
        print("❌ لم يتم العثور على أي ملفات .session! الرجاء رفع الملفات أولاً.")
        return

    print(f"📂 تم العثور على {len(session_files)} ملفات جلسة. جاري التشغيل...")
    
    # إنشاء مهمة مستقلة لكل ملف جلسة
    tasks = [run_worker(file) for file in session_files]
    
    # تشغيلهم جميعاً في وقت واحد
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    # تشغيل سيرفر الويب في الخلفية
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    # تشغيل البوتات
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
