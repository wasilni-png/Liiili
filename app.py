from telethon import TelegramClient, events
import re
from telethon.sessions import StringSession

# اجلب النص من متغيرات البيئة في Render
session_str = "1BJWap1sBu40j3ZH7Al9W21d4ghtN5RRH8mHEvqNj2MnWyhv1DVOLP86bxbf4BGk3bnuFeLCQVPKBvO2TRT8f5DWsTq-Qo8guDA0n2F6Zsb-dod4hEm3AeszVGzQp3JQmyk3HgmT2YB7hlMuA2ebcYO1jo_nRWu8Ib7ENq8XpjaTYtcrRhUfDgMBGg6ySQjhZWs4ICnAk79o3T9ICewTxZg6O2BlJMpP6kQThQRyWHGaytoadkvoL5tJcnrivDgsUSfY5r4IzrTE00RH9F7dTbuu9jeLqb2WKDZXcCM88_8gQGrB0etCtFZD7UnHydyQagi3i7pZZimgHOb_s8Xd7xPFjaP8Vuf4=" 



# --- إعدادات الحساب ---
# ضع بياناتك التي حصلت عليها من my.telegram.org هنا
api_id = 33888256  # استبدل هذا برقمك
api_hash = 'bb1902689a7e203a7aedadb806c08854' # استبدل هذا بالكود الخاص بك

# اسم الجلسة (سيتم إنشاء ملف بهذا الاسم لحفظ تسجيل الدخول)
client = TelegramClient(StringSession(session_str), api_id, api_hash)

# الكلمات المفتاحية التي نبحث عنها
keywords = ['شهري', 'بالشهر', 'شهريا', 'شهرياً']

@client.on(events.NewMessage)
async def my_event_handler(event):
    # 1. التأكد أن الرسالة قادمة من مجموعة (وليس محادثة خاصة)
    if not event.is_group:
        return

    # الحصول على نص الرسالة
    message_text = event.raw_text
    
    # إذا لم يكن هناك نص (مثلاً صورة فقط)، تجاهل الأمر
    if not message_text:
        return

    # 2. البحث عن الكلمات المفتاحية داخل الرسالة
    # نستخدم any للتحقق مما إذا كانت أي كلمة من القائمة موجودة في النص
    if any(keyword in message_text for keyword in keywords):
        
        try:
            # الحصول على معلومات المرسل (العميل)
            sender = await event.get_sender()
            sender_id = sender.id
            sender_name = sender.first_name if sender.first_name else "مستخدم"
            
            # رابط حساب العميل
            user_link = f"tg://user?id={sender_id}"
            
            # رابط الرسالة الأصلية (يعمل بشكل تلقائي في تيليثون)
            message_link = ""
            if event.message.id:
                 # محاولة جلب رابط الرسالة (يعتمد على نوع المجموعة عامة أو خاصة)
                 chat = await event.get_chat()
                 if hasattr(chat, 'username') and chat.username:
                     message_link = f"https://t.me/{chat.username}/{event.message.id}"
                 else:
                     # للمجموعات الخاصة، الرابط يكون معقداً قليلاً، لذا نستخدم رابط القناة الداخلي
                     # ملاحظة: في المجموعات الخاصة جداً قد لا يعمل الرابط للمستخدمين من الخارج
                     message_link = f"https://t.me/c/{chat.id}/{event.message.id}"

            # 3. تجهيز الرسالة التي سيتم إرسالها للرسائل المحفوظة
            saved_msg_content = (
                f"🚨 **تم رصد رسالة جديدة!**\n\n"
                f"👤 **العميل:** [{sender_name}]({user_link})\n"
                f"🔗 **رابط الرسالة:** [اضغط هنا للذهاب للرسالة]({message_link})\n\n"
                f"📝 **محتوى الرسالة:**\n"
                f"`{message_text}`"
            )

            # 4. الإرسال إلى "الرسائل المحفوظة" (me)
            await client.send_message('me', saved_msg_content, link_preview=False)
            
            print(f"تم حفظ رسالة من {sender_name}")

        except Exception as e:
            print(f"حدث خطأ: {e}")

# تشغيل البوت
print("جاري تشغيل اليوزى بوت... يرجى الانتظار")
client.start()
client.run_until_disconnected()
