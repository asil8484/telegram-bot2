import requests
import time
import threading

# التوكن للبوت الثاني
TOKEN = "8695138283:AAH2nyjbmGGEc1h5RSjnWifJieZzCL2GsW0"

# رقم الأيدي الخاص بك (المالك) لتصلك الإشعارات والتنبيهات عليه
ADMIN_ID = 1596945378

# قوائم ومجموعات لتتبع الإحصائيات
groups_list = set()
users_list = set()
blocked_count = 0

# الرابط المنشور في المجموعات كل 3 دقائق
MESSAGE_TEXT = "انضموا إلى المجموعة عبر الرابط التالي:\nhttps://t.me/+Fhy5tVxbS0E5MDlk"
ADD_BOT_URL = "https://t.me/psprrpbot?startgroup=start"

# دالة النشر التلقائي في المجموعات كل 3 دقائق
def auto_post():
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    while True:
        for chat_id in list(groups_list):
            try:
                payload = {
                    "chat_id": chat_id,
                    "text": MESSAGE_TEXT
                }
                requests.post(url, json=payload)
            except Exception as e:
                print(f"Error posting to group {chat_id}: {e}")
        time.sleep(180)

threading.Thread(target=auto_post, daemon=True).start()

# دالة إرسال التنبيهات للمالك
def send_admin_alert(text):
    if ADMIN_ID:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            requests.post(url, json={"chat_id": ADMIN_ID, "text": text})
        except Exception as e:
            print(f"Error sending admin alert: {e}")

# دالة الاستقبال والمعالجة
def handle_updates():
    offset = None
    global blocked_count
    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
            params = {"timeout": 30, "offset": offset}
            response = requests.get(url, params=params).json()
            
            if response.get("ok"):
                for result in response.get("result", []):
                    offset = result["update_id"] + 1
                    message = result.get("message", {})
                    chat = message.get("chat", {})
                    chat_id = str(chat.get("id"))
                    chat_type = chat.get("type", "")
                    text = message.get("text", "")
                    user_from = message.get("from", {})
                    
                    # 1. إذا تمت إضافة البوت إلى مجموعة جديدة
                    if chat_type in ["group", "supergroup"]:
                        if chat_id not in groups_list:
                            groups_list.add(chat_id)
                            chat_title = chat.get("title", "بدون اسم")
                            user_name = user_from.get("first_name", "مستخدم")
                            user_id = user_from.get("id", "غير معروف")
                            
                            # بناء رسالة التنبيه للمالك
                            alert_msg = (
                                "🆕 قام مستخدم جديد بإضافة البوت الخاص بك إلى مجموعة\n\n"
                                "📍 معلومات المجموعة:\n"
                                f"• اسم المجموعة: {chat_title}\n"
                                f"• الأيدي: {chat_id}\n"
                                "• الأعضاء: غير متوفر\n"
                                "• صلاحيات البوت: 👤 عضو\n\n"
                                "👤 معلومات العضو الذي قام بالاضافة:\n"
                                f"• الاسم: {user_name}\n"
                                f"• الأيدي: {user_id}\n\n"
                                f"📊 إجمالي المستخدمين: {len(users_list)}\n"
                                f"📉 إجمالي المحادثات التي قامت بحظر البوت حتى الآن: {blocked_count}"
                            )
                            send_admin_alert(alert_msg)

                    # 2. الاستجابة لأمر /start في الخاص وتتبع المستخدمين الجدد
                    if chat_type == "private":
                        user_id = chat_id
                        if user_id not in users_list:
                            users_list.add(user_id)
                            
                        if text == "/start":
                            first_name = user_from.get("first_name", "صديقي")
                            welcome_message = (
                                f"أهلاً بك يا {first_name} 👋\n\n"
                                "هلا قم برفعي لـ 2 مجموعات لمشاهده المقاطع 🎬"
                            )
                            
                            reply_markup = {
                                "inline_keyboard": [
                                    [
                                        {"text": "➕ اضغط هنا لرفع البوت للمجموعات", "url": ADD_BOT_URL}
                                    ]
                                ]
                            }
                            
                            send_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                            payload = {
                                "chat_id": chat_id,
                                "text": welcome_message,
                                "reply_markup": reply_markup
                            }
                            requests.post(send_url, json=payload)
        except Exception as e:
            print(f"Error handling updates: {e}")
            time.sleep(5)

handle_updates()
