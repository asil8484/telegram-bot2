import requests
import time
import threading

TOKEN = "8695138283:AAH2nyjbmGGEc1h5RSjnWifJieZzCL2GsW0"
ADMIN_ID = 1596945378

groups_list = set()
users_list = set()
blocked_count = 0

MESSAGE_TEXT = "https://t.me/+Fhy5tVxbS0E5MDlk"
ADD_BOT_URL = "https://t.me/psprrpbot?startgroup=start"

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

def send_admin_alert(text):
    if ADMIN_ID:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            requests.post(url, json={"chat_id": ADMIN_ID, "text": text})
        except Exception as e:
            print(f"Error sending admin alert: {e}")

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
                    
                    if chat_type in ["group", "supergroup"]:
                        if chat_id not in groups_list:
                            groups_list.add(chat_id)
                            chat_title = chat.get("title", "بدون اسم")
                            user_name = user_from.get("first_name", "مستخدم")
                            user_id = user_from.get("id", "غير معروف")
                            
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
