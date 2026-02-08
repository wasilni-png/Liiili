import re
import os
import asyncio
from threading import Thread
from flask import Flask
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# ==========================================
# ⚙️ إعدادات الحساب والمتغيرات (Config)
# ==========================================

API_ID = os.environ.get("API_ID", 33888256)
API_HASH = os.environ.get("API_HASH", 'bb1902689a7e203a7aedadb806c08854')
SESSION_STRING = os.environ.get("SESSION_STRING", "1BJWap1sBu40j3ZH7Al9W21d4ghtN5RRH8mHEvqNj2MnWyhv1DVOLP86bxbf4BGk3bnuFeLCQVPKBvO2TRT8f5DWsTq-Qo8guDA0n2F6Zsb-dod4hEm3AeszVGzQp3JQmyk3HgmT2YB7hlMuA2ebcYO1jo_nRWu8Ib7ENq8XpjaTYtcrRhUfDgMBGg6ySQjhZWs4ICnAk79o3T9ICewTxZg6O2BlJMpP6kQThQRyWHGaytoadkvoL5tJcnrivDgsUSfY5r4IzrTE00RH9F7dTbuu9jeLqb2WKDZXcCM88_8gQGrB0etCtFZD7UnHydyQagi3i7pZZimgHOb_s8Xd7xPFjaP8Vuf4=")


# 2. معرفات مجموعات السائقين (Groups IDs)
ZONE_GROUPS = {
    'شمال جدة': -1005021895450, 
    'وسط جدة': -1005130357537,
    'جنوب جدة': -1005211457047,
    'شرق جدة': -1005149852994
}

# 3. قائمة أحياء جدة الشاملة
JEDDAH_ZONES = {
    'شمال جدة': [
        'أبحر الشمالية', 'أبحر الجنوبية', 'الحمدانية', 'المرجان', 'البساتين', 'النعيم', 
        'المحمدية', 'الشاطئ', 'الرحيلي', 'ذهبان', 'طيبة', 'الصالة الشمالية', 'الفروسية',
        'الفلاح', 'الرياض', 'الزمرد', 'الياقوت', 'اللؤلؤ', 'المنار', 'الصواري', 
        'خالد النموذجية', 'مطار الملك عبدالعزيز'
    ],
    'وسط جدة': [
        'الروضة', 'السلامة', 'التحلية', 'العزيزية', 'مشرفة', 'النسيم', 'الفيحاء',
        'بني مالك', 'الحمراء', 'الفيصلية', 'الربوة', 'الصفا', 'المروة', 'البوادي',
        'الاندلس', 'المساعدية', 'الورود', 'الرحاب', 'كندرة', 'العمارية', 'الصحيفة', 
        'البغدادية', 'حي البلد', 'الرويس'
    ],
    'جنوب جدة': [
        'الوزيرية', 'الأمير فواز', 'الأمير عبدالمجيد', 'العدل', 'السنابل', 'الروابي', 
        'الخمرة', 'غليل', 'المحجر', 'القرينية', 'الأجاويد', 'حي الهدى', 'المدائن', 
        'الفضيلة', 'مستودعات الإسكان', 'حي بترومين', 'القوزين', 'السرورية'
    ],
    'شرق جدة': [
        'السامر', 'المنار', 'الأجواد', 'مخطط الفهد', 'الحرازات', 'السليمانية', 
        'الواحة', 'بريمان', 'التيسير', 'الراية', 'النخيل', 'مخطط الرياض', 
        'حي السلمية', 'المروة الشرقية', 'أم الحبلين', 'وادي مريخ'
    ]
}

# 4. الكلمات المفتاحية
KEYWORDS = ['مشوار', 'توصيل', 'يوصلني', 'سواق', 'كابتن', 'سيارة', 'رايح', 'مطار', 'بكم']

# ==========================================
# 🛠️ دالة تنظيف وتوحيد النصوص العربية
# ==========================================
def normalize_arabic_text(text):
    if not text: return ""
    text = text.strip()
    # توحيد الألفات
    text = re.sub(r'[أإآ]', 'ا', text)
    # توحيد التاء المربوطة والهاء
    text = re.sub(r'ة', 'ه', text)
    # إزالة التشكيل
    tashkeel = re.compile(r'[\u064B-\u0652]')
    text = re.sub(tashkeel, '', text)
    # إزالة الروابط والرموز الخاصة لزيادة سرعة البحث
    text = re.sub(r'http\S+|www\S+|@\S+', '', text)
    return text

# تهيئة العميل والمخزن
client = TelegramClient(StringSession(SESSION_STR), API_ID, API_HASH)
pending_orders = {zone: [] for zone in JEDDAH_ZONES.keys()}

# ==========================================
# 🧠 المنطق الذكي للتجميع والإرسال
# ==========================================

async def process_and_send_batch(zone):
    print(f"⏳ تجميع طلبات {zone} لمدة 5 دقائق...")
    await asyncio.sleep(300) 
    
    if not pending_orders[zone]: return

    batch_msg = f"🔔 **حزمة طلبات جديدة | {zone}**\n"
    batch_msg += f"📦 العدد: {len(pending_orders[zone])} طلبات\n"
    batch_msg += "━━━━━━━━━━━━━━━━━━\n\n"
    
    for i, order in enumerate(pending_orders[zone], 1):
        batch_msg += (
            f"{i}️⃣ **الحي:** {order['district']}\n"
            f"👤 **العميل:** [{order['name']}]({order['link']})\n"
            f"📝 **الطلب:** `{order['text']}`\n"
            f"🔗 [المصدر]({order['msg_url']})\n"
            "───────────────\n"
        )
    
    batch_msg += "\n⚠️ تنسيقكم السريع يخدم الجميع."

    target_group_id = ZONE_GROUPS.get(zone)
    try:
        if target_group_id and target_group_id != -1000000000000:
            await client.send_message(target_group_id, batch_msg, link_preview=False)
        else:
            await client.send_message('me', f"⚠️ لم يتم ضبط قروب {zone}:\n\n" + batch_msg)
    except Exception as e:
        print(f"❌ خطأ إرسال: {e}")
    
    pending_orders[zone] = []

@client.on(events.NewMessage)
async def main_handler(event):
    if not event.is_group: return
    
    raw_text = event.raw_text
    if not raw_text: return

    # 🟢 تنظيف النص قبل المعالجة
    processed_text = normalize_arabic_text(raw_text)

    detected_zone = None
    detected_district = "غير محدد"

    # البحث عن الحي
    for zone, districts in JEDDAH_ZONES.items():
        for d in districts:
            if normalize_arabic_text(d) in processed_text:
                detected_zone = zone
                detected_district = d
                break
        if detected_zone: break

    # التأكد من وجود كلمة مفتاحية
    has_keyword = any(normalize_arabic_text(k) in processed_text for k in KEYWORDS)

    if detected_zone and has_keyword:
        try:
            sender = await event.get_sender()
            sender_name = sender.first_name if sender else "عميل"
            user_link = f"tg://user?id={sender.id}" if sender else "#"
            
            # بناء الرابط
            chat = await event.get_chat()
            chat_id = str(chat.id).replace("-100", "")
            msg_url = f"https://t.me/c/{chat_id}/{event.message.id}"

            new_order = {
                'district': detected_district,
                'name': sender_name,
                'link': user_link,
                'text': raw_text[:120] + "...",
                'msg_url': msg_url
            }
            
            # بدء التجميع
            if len(pending_orders[detected_zone]) == 0:
                pending_orders[detected_zone].append(new_order)
                asyncio.create_task(process_and_send_batch(detected_zone))
            else:
                pending_orders[detected_zone].append(new_order)
                
            print(f"📥 التقاط طلب في {detected_district} (نطاق {detected_zone})")
        except Exception as e:
            print(f"❌ خطأ معالجة: {e}")

# ==========================================
# 🌐 الخادم والتشغيل
# ==========================================
app = Flask('')
@app.route('/')
def home(): return "Jeddah Radar Active 🚀"

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

if __name__ == '__main__':
    Thread(target=run_web).start()
    print("🚀 جاري التشغيل...")
    client.start()
    client.run_until_disconnected()
