import asyncio
import threading
import sys
import os
import logging
import re
import math
from flask import Flask
from pyrogram import Client
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
import google.generativeai as genai
from datetime import datetime

# ==========================================
# ⚙️ الإعدادات والمتغيرات (Config)
# ==========================================
try:
    from config import normalize_text, CITIES_DISTRICTS, BOT_TOKEN
    print("✅ تم تحميل الإعدادات بنجاح")
except Exception as e:
    print(f"❌ خطأ في تحميل ملف config.py: {e}")
    sys.exit(1)

# --- متغيرات البيئة ---
# إعدادات السجلات
logging.basicConfig(level=logging.WARNING)

# متغيرات البيئة (تأكد من تعبئتها في الاستضافة)
API_ID = os.environ.get("API_ID", "36360458")
API_HASH = os.environ.get("API_HASH", "daae4628b4b4aac1f0ebfce23c4fa272")
SESSION_STRING = os.environ.get("SESSION_STRING", "BAIq0QoAOD9QpM8asjl1fICVx0vTRH7QjtgTNCEF692Ihz9Xkj_HWnZ6hnl3pv8gN6yFWqMEBhFl7A40uQWQWIsU8KM9or6K-_HsGbe8SP_4AhbIIFU7vrqyo_tuU0SydmvpT8sbSs-RC-yl89Gm5t4EXag2g9Wxr_MQaWIYtJZGWWkVisaDjM8AnUbfD9BDzolvp06qEz-mnsrKZCQKmrPmA_LNhxpqBBcdEJ9EVs4Lwvsh0B7u_ZyOtLhetuwb1YAd1pYNYd00OGwlLuH-8tJc5v5cFbeX6bxT89JMEZVELD2aKhU1XeljAxSieD0F3yL9TsLFglGwu-qsSs7b_073w9e9ZAAAAAH-ZrzOAA")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyDtF2lEZuEvI1hTFFrPRbGwwvj7ZocdPjs")

# إعدادات المستخدمين والقنوات
# 🛠️ قائمة الـ IDs المحدثة (المستلمين المحددين فقط)
TARGET_USERS = [
    7996171713, 7513630480
]

CHANNEL_ID = -1003843717541 

# ==========================================
# 🗺️ البيانات الجغرافية (من الكودAIzaSyDtF2lEZuEvI1hTFFrPRbGwwvj7ZocdPjs الأول)
# ==========================================
# ملاحظة: يمكنك إضافة أحياء المدينة المنورة هنا بنفس التنسيق ليقوم البوت بحساب المسافة لها أيضاً
DISTRICT_COORDS = {
    'أبحر الشمالية': (21.7511, 39.1235), 'أبحر الجنوبية': (21.7144, 39.1256),
    'الحمدانية': (21.7831, 39.2161), 'المرجان': (21.7011, 39.1022),
    'البساتين': (21.6885, 39.1255), 'النعيم': (21.6255, 39.1550),
    'المحمدية': (21.6500, 39.1350), 'الشاطئ': (21.6100, 39.1150),
    'الرحيلي': (21.8200, 39.1500), 'ذهبان': (21.9333, 39.1167),
    'طيبة': (21.8000, 39.1800), 'الصالة الشمالية': (21.6950, 39.1620),
    'الفروسية': (21.8150, 39.2250), 'الفلاح': (21.7900, 39.2300),
    'الرياض': (21.8450, 39.2350), 'الزمرد': (21.7750, 39.1100),
    'الياقوت': (21.7650, 39.1150), 'اللؤلؤ': (21.7450, 39.1050),
    'الصواري': (21.7850, 39.1250), 'خالد النموذجية': (21.7200, 39.1850),
    'مطار الملك عبدالعزيز': (21.6833, 39.1500), 'الأمواج': (21.7300, 39.1100),
    'الفردوس': (21.7400, 39.1200), 'الشراع': (21.7250, 39.1150),
    'المنارات': (21.7100, 39.1300), 'الصالحية': (21.7950, 39.2100),
    'الماجد': (21.8050, 39.2200), 'السلطان': (21.8100, 39.2150),
    'النزهة': (21.6400, 39.1700), 'الروضة': (21.5667, 39.1500), 
    'السلامة': (21.5833, 39.1500), 'التحلية': (21.5510, 39.1650), 
    'العزيزية': (21.5450, 39.1850), 'مشرفة': (21.5350, 39.1950), 
    'النسيم': (21.5050, 39.2250), 'الفيحاء': (21.4950, 39.2350), 
    'بني مالك': (21.5150, 39.2150), 'الحمراء': (21.5200, 39.1550), 
    'الفيصلية': (21.5750, 39.1750), 'الربوة': (21.5950, 39.1850), 
    'الصفا': (21.5850, 39.2050), 'المروة': (21.6150, 39.2050), 
    'البوادي': (21.5950, 39.1650), 'الاندلس': (21.5400, 39.1450), 
    'المساعدية': (21.5300, 39.1700), 'الورود': (21.5250, 39.2150), 
    'الرحاب': (21.5550, 39.2150), 'كندرة': (21.4950, 39.2050), 
    'العمارية': (21.4880, 39.1950), 'الصحيفة': (21.4850, 39.1900), 
    'البغدادية': (21.4950, 39.1850), 'حي البلد': (21.4833, 39.1833), 
    'الرويس': (21.5100, 39.1650), 'الهنداوية': (21.4750, 39.1800), 
    'الثعالبة': (21.4650, 39.1850), 'القريات': (21.4600, 39.1900), 
    'السبيل': (21.4700, 39.1900), 'الوزيرية': (21.4600, 39.2350), 
    'الأمير فواز': (21.4250, 39.2650), 'الأمير عبدالمجيد': (21.4050, 39.2750), 
    'العدل': (21.4550, 39.2550), 'السنابل': (21.3650, 39.2850), 
    'الروابي': (21.4750, 39.2550), 'الخمرة': (21.3000, 39.2200), 
    'غليل': (21.4450, 39.2050), 'المحجر': (21.4400, 39.1950), 
    'القرينية': (21.3250, 39.2350), 'الأجاويد': (21.3850, 39.2850), 
    'حي الهدى': (21.3950, 39.2550), 'المدائن': (21.3500, 39.2450), 
    'الفضيلة': (21.3150, 39.2550), 'مستودعات الإسكان': (21.4150, 39.2250), 
    'حي بترومين': (21.4350, 39.1850), 'القوزين': (21.2850, 39.2050), 
    'السرورية': (21.3350, 39.1950), 'المرسلات': (21.4000, 39.2400), 
    'الهدى 2': (21.3800, 39.2600), 'السامر': (21.6050, 39.2450), 
    'المنار': (21.6050, 39.2300), 'الأجواد': (21.6150, 39.2550), 
    'مخطط الفهد': (21.6250, 39.2650), 'الحرازات': (21.4550, 39.3650), 
    'السليمانية': (21.4950, 39.2450), 'الواحة': (21.5650, 39.2450), 
    'بريمان': (21.6550, 39.2550), 'التيسير': (21.5750, 39.2750), 
    'الراية': (21.6250, 39.2750), 'النخيل': (21.5250, 39.2650), 
    'مخطط الرياض': (21.8450, 39.2350), 'حي السلمية': (21.4450, 39.2850), 
    'المروة الشرقية': (21.6250, 39.2150), 'أم الحبلين': (21.5850, 39.2950), 
    'وادي مريخ': (21.5450, 39.3050), 'مخطط مريخ': (21.5500, 39.3100), 
    'مخطط المصباح': (21.5900, 39.2600)
}

# قوائم الفلترة (من الكود الثاني - محدثة)
BLOCK_KEYWORDS = [
    "متواجد", "متاح", "شغال", "جاهز", "أسعارنا", "سيارة نظيفة", "نقل عفش", 
    "دربك سمح", "توصيل مشاوير", "أوصل", "اوصل", "اتصال", "واتساب", "للتواصل",
    "خاص", "الخاص", "بخدمتكم", "خدمتكم", "أستقبل", "استقبل", "نقل بضائع",
    "مشاويركم", "سياره نظيفه", "فان", "دباب", "سطحه", "سطحة", "كابتن", 
    "مندوب", "مناديب", "توصيل طلبات", "ارخص الأسعار", "أرخص الأسعار", "بأسعار",
    "عقار", "عقارات", "للبيع", "للإيجار", "للايجار", "دور", "شقة", "شقه",
    "رخصة فال", "رخصة", "رخصه", "مخطط", "أرض", "ارض", "فلة", "فله", 
    "عماره", "عمارة", "استثمار", "صك", "إفراغ", "الوساطة العقارية", "تجاري", "سكني",
    "اشتراك", "باقات", "تسجيل", "تأمين", "تفويض", "تجديد", "قرض", "تمويل", 
    "بنك", "تسديد", "مخالفات", "اعلان", "إعلان", "قروب", "مجموعة", "انضم", 
    "رابط", "نشر", "قوانين", "احترام", "الذوق العام", "استقدام", "خادمات",
    "تعقيب", "معقب", "انجاز", "إنجاز", "كفيل", "نقل كفالة", "اسقاط", "تعديل مهنة",
    "حياك الله", "نورتنا", "انضمامك", "أهلاً بك", "اهلا بك", "قواعد المجموعة",
    "مرحباً بك", "مرحبا بك", "تنبيه", "محظور", "يُمنع", "يمنع", "بالتوفيق للجميع",
    "http", "t.me", ".com", "رابط القناة", "اخلاء مسؤولية", "ذمة",
    "استثمار", "زواج", "مسيار", "خطابه", "خطابة"
]

IRRELEVANT_TOPICS = [
    "عيادة", "عياده", "اسنان", "أسنان", "دكتور", "طبيب", "مستشفى", "مستوصف",
    "علاج", "تركيب", "تقويم", "خلع", "حشو", "تنظيف", "استفسار", "افضل", "أفضل",
    "تجربة", "مين جرب", "رأيكم", "تنصحون", "ورشة", "سمكري", "قطع غيار",
    "عذر طبي", "سكليف", "سكليفات"
]

# ==========================================
# 🧠 دوال المساعدة (Logic Helpers)
# ==========================================

def normalize_text(text):
    if not text: return ""
    text = re.sub(r'[أإآ]', 'ا', text)
    text = re.sub(r'ة', 'ه', text)
    text = re.sub(r'ى', 'ي', text)
    return text

def extract_smart_details(text):
    """استخراج السعر وعدد الركاب (من الكود الأول)"""
    price_match = re.search(r'(\d{1,4})\s?(ريال|ر|السعر|دفع)', text)
    passengers_match = re.search(r'(عدد|احنا|ركاب)\s?(\d)', text)

    price = price_match.group(1) if price_match else None
    passengers = passengers_match.group(2) if passengers_match else None
    return price, passengers

def calculate_distance(origin_name, dest_name):
    """حساب المسافة والوقت بناءً على الإحداثيات (من الكود الأول)"""
    # تنظيف المدخلات لمحاولة إيجاد تطابق في القاموس
    norm_origin = normalize_text(origin_name)
    norm_dest = normalize_text(dest_name)
    
    # البحث عن المفاتيح في القاموس
    coords1 = None
    coords2 = None
    
    # محاولة مطابقة مرنة
    for k, v in DISTRICT_COORDS.items():
        if normalize_text(k) in norm_origin: coords1 = v
        if normalize_text(k) in norm_dest: coords2 = v
    
    if not coords1 or not coords2: return None, None

    lat1, lon1 = coords1
    lat2, lon2 = coords2
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    actual_dist = round(R * c * 1.3, 1) # ضرب في 1.3 لتقدير تعرجات الطرق
    est_time = round((actual_dist / 40) * 60) + 5 # متوسط سرعة 40 كم/س
    return actual_dist, est_time

# ==========================================
# 🤖 الذكاء الاصطناعي (Gemini Logic)
# ==========================================

genai.configure(api_key=GEMINI_API_KEY)
ai_model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config={"temperature": 0.1, "max_output_tokens": 5}
)

async def analyze_message_hybrid(text):
    if not text or len(text) < 5 or len(text) > 400: return False

    clean_text = normalize_text(text)
    
    # الفلتر المحلي السريع (Local Filter)
    if any(k in clean_text for k in BLOCK_KEYWORDS): return False
    if any(k in clean_text for k in IRRELEVANT_TOPICS): return False

    # البرومبت الشامل (Master Prompt)
        # برومبت متخصص لخدمات التوصيل في مدينة جدة
    prompt = f"""
    Role: You are an elite AI Traffic Controller specialized in Jeddah City geography and taxi market.
    Objective: Filter messages to identify REAL CUSTOMERS in Jeddah seeking rides, school transport, or logistics.
    
    [STRICT ANALYSIS RULES]
    - SENDER = CUSTOMER (Needs service) -> Reply 'YES'
    - SENDER = DRIVER (Offers service) -> Reply 'NO'
    - SENDER = SPAM/ADVERTISEMENT -> Reply 'NO'

    [✅ CLASSIFY AS 'YES' (JEDDAH CUSTOMER REQUESTS)]
    1. Ride Needs: (e.g., "أبغى سيارة للمطار", "كابتن مشوار لأبحر", "توصيل للبلد").
    2. Jeddah Routes: Text mentioning Jeddah paths (e.g., "من السامر للتحلية", "من الحمدانية للرويس", "إلى واجهة جدة البحرية").
    3. Airport & Train: (e.g., "توصيل مطار الملك عبدالعزيز", "مشوار لمحطة قطار السليمانية").
    4. School & Daily Commute: Very common in Jeddah (e.g., "توصيل طالبات لجامعة الملك عبدالعزيز", "نقل موظفات لحي الشاطئ", "عقد شهري دوام").
    5. Specific Jeddah Landmarks: Mentioning places like (Red Sea Mall, Al-Balad, Tahlia Street, Obhur, Corniche, Serafi Mega Mall).
    6. Delivery: (e.g., "توصيل غرض من شرق جدة لغربها").

    [❌ CLASSIFY AS 'NO' (IGNORE THESE)]
    1. Jeddah Driver Ads: (e.g., "سواق خاص بجدة متاح", "توصيل مشاوير بسيارة نظيفة", "كابتن جاهز بجدة").
    2. Non-Logistics Topics: (Medical excuses/Sick leaves, Marriage/Misyar, Real Estate, Loans).
    3. General Chat: (e.g., "كيف زحمة طريق الحرمين؟", "صباح الخير يا أهل جدة").

    [📍 JEDDAH GEOGRAPHIC CONTEXT]
    Recognize these districts: (Hamdaniya, Obhur, Samer, Safa, Rawdah, Salamah, Zahra, Naeem, Aziziyah, Faihaa, Gawhara, Sanabel).

    [DECISION LOGIC]
    - "من حي السامر إلى المطار" -> YES
    - "أنا كابتن متواجد في أبحر" -> NO
    - "مطلوب باص لتوصيل مدارس في الحمدانية" -> YES
    - "استثمار عقاري في جدة" -> NO

    Input Text: "{text}"
    FINAL ANSWER (Reply ONLY with 'YES' or 'NO'):
    """


    try:
        response = await asyncio.to_thread(ai_model.generate_content, prompt)
        return "YES" in response.text.strip().upper()
    except Exception as e:
        print(f"⚠️ تجاوز AI: {e}")
        # احتياطي يدوي (Regex)
        return any(w in clean_text for w in ["سواق", "توصيل", "مشوار", "ابي", "ابغى", "مطلوب"])

# ==========================================
# 📨 نظام الإرسال الموحد (Dispatch System)
# ==========================================

user_app = Client("my_session", session_string=SESSION_STRING, api_id=API_ID, api_hash=API_HASH)
bot_sender = Bot(token=BOT_TOKEN)

async def process_and_send(original_msg, origin="عام", dest="غير محدد"):
    content = original_msg.text or original_msg.caption
    customer = original_msg.from_user
    customer_id = customer.id if customer else 0
    msg_id = original_msg.id
    chat_id_raw = original_msg.chat.id
    chat_id_clean = str(chat_id_raw).replace("-100", "")
    bot_username = "Mishwariibot" # استبدله بيوزر بوتك الصحيح

    # 1. استخراج المعلومات الذكية (سعر، ركاب، مسافة)
    price, passengers = extract_smart_details(content)
    dist, time = calculate_distance(origin, dest)

    # تجهيز النص الإضافي
    extra_info = ""
    if price: extra_info += f"💰 <b>السعر المقترح:</b> {price} ريال\n"
    if passengers: extra_info += f"👥 <b>الركاب:</b> {passengers}\n"
    if dist: extra_info += f"📏 <b>المسافة:</b> {dist} كم (~{time} دقيقة)\n"

    # 2. الإرسال للقناة العامة (روابط محمية)
    gate_contact = f"https://t.me/{bot_username}?start=contact_{customer_id}_{msg_id}"
    gate_source = f"https://t.me/{bot_username}?start=source_{chat_id_raw}_{msg_id}"
    
    channel_btns = InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 مراسلة العميل (للمشتركين)", url=gate_contact)],
        [InlineKeyboardButton("🔗 مصدر الطلب (للمشتركين)", url=gate_source)],
        [InlineKeyboardButton("💳 للاشتراك وتفعيل الحساب", url="https://t.me/x3FreTx")]
    ])

    base_text = (
        f"🎯 <b>طلب مشوار جديد</b>\n\n"
        f"📍 <b>من:</b> {origin}\n"
        f"🏁 <b>إلى:</b> {dest}\n"
        f"{extra_info}"
        f"📝 <b>النص:</b> <i>{content[:200]}</i>\n\n"
        f"⏰ <b>{datetime.now().strftime('%H:%M')}</b>"
    )

    try:
        await bot_sender.send_message(chat_id=CHANNEL_ID, text=base_text, reply_markup=channel_btns, parse_mode=ParseMode.HTML)
    except Exception as e: print(f"❌ خطأ القناة: {e}")

    # 3. الإرسال للمستخدمين المحددين (روابط مباشرة)
    direct_contact = f"https://t.me/{customer.username}" if customer and customer.username else f"tg://user?id={customer_id}"
    direct_source = f"https://t.me/c/{chat_id_clean}/{msg_id}"

    user_btns = InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 مراسلة العميل مباشرة", url=direct_contact)],
        [InlineKeyboardButton("🔗 الذهاب للمصدر", url=direct_source)]
    ])

    for user_id in TARGET_USERS:
        try:
            await bot_sender.send_message(chat_id=user_id, text=f"🚀 <b>طلب خاص لك:</b>\n\n{base_text}", reply_markup=user_btns, parse_mode=ParseMode.HTML)
        except Exception as e: print(f"⚠️ فشل إرسال لـ {user_id}: {e}")

# ==========================================
# 📡 الرادار الرئيسي (Main Loop)
# ==========================================

async def start_radar():
    await user_app.start()
    print("🚀 الرادار المدمج (Super Bot) يعمل الآن...")
    
    # رسالة تنبيه عند البدء
    if TARGET_USERS:
        try:
            await bot_sender.send_message(TARGET_USERS[-1], "✅ تم تشغيل البوت بنظامه الجديد")
        except: pass

    last_processed = {}

    while True:
        try:
            await asyncio.sleep(4) # انتظار لتقليل الضغط
            async for dialog in user_app.get_dialogs(limit=50):
                if str(dialog.chat.type).upper() not in ["GROUP", "SUPERGROUP"]: continue
                
                chat_id = dialog.chat.id
                async for msg in user_app.get_chat_history(chat_id, limit=1):
                    if chat_id in last_processed and msg.id <= last_processed[chat_id]: continue
                    last_processed[chat_id] = msg.id
                    
                    text = msg.text or msg.caption
                    if not text or (msg.from_user and msg.from_user.is_self): continue

                    # 1. التحليل بالذكاء الاصطناعي
                    if await analyze_message_hybrid(text):
                        
                        # 2. محاولة استخراج المناطق (Origin/Dest) من النص
                        origin_found = "غير محدد"
                        dest_found = "غير محدد"
                        
                        text_norm = normalize_text(text)
                        
                        # بحث بسيط عن المناطق في القاموس
                        # (يمكن تطوير هذا الجزء ليكون أذكى باستخدام "من" و "إلى")
                        tokens = text_norm.split()
                        matches = []
                        for district in DISTRICT_COORDS.keys():
                            d_norm = normalize_text(district)
                            if d_norm in text_norm:
                                matches.append(district)
                        
                        # تخمين المنطلق والوجهة
                        if len(matches) >= 1: origin_found = matches[0]
                        if len(matches) >= 2: dest_found = matches[1]
                        
                        # في حال لم يجد مناطق من القاموس، يحاول البحث عن كلمة بعد "من"
                        if origin_found == "غير محدد":
                             m_from = re.search(r'من\s+(\w+)', text_norm)
                             if m_from: origin_found = m_from.group(1)

                        await process_and_send(msg, origin=origin_found, dest=dest_found)

        except Exception as e:
            print(f"⚠️ خطأ في الدورة: {e}")
            await asyncio.sleep(5)

# ==========================================
# 🌐 تشغيل السيرفر (Flask Server)
# ==========================================

app = Flask('')

@app.route('/')
def home():
    return "✅ Super Bot Logic is Active & Running."

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    asyncio.run(start_radar())
