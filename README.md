# 🛠️ Helpdesk & Support Management System

نظام متطور لإدارة تذاكر الدعم الفني، مبني باستخدام **Django 5.x**، ومحمي بواسطة **Nginx** و **SSL**. تم تصميمه لتنظيم طلبات الدعم، توزيع المهام، ومتابعة سير العمل باحترافية كاملة.
A Django-based helpdesk and support ticket management system.  
This project is designed to manage support requests, assign tasks, and track progress in an organized way.
---

## 🚀 الميزات الرئيسية (Key Features)

* **نظام توثيق متقدم:** تسجيل دخول/خروج وإدارة جلسات المستخدمين.
* **تكامل Azure AD:** دعم تسجيل الدخول الموحد (SSO) عبر حسابات Microsoft.
* **إدارة التذاكر:** إنشاء، تحديث، ومتابعة دورة حياة الطلبات (مفتوح، قيد التنفيذ، تم الحل، مغلق).
* **التصنيف والأولويات:** تنظيم التذاكر بناءً على القسم ودرجة الأهمية.
* **دعم اللغات:** واجهة مستخدم ثنائية اللغة (عربي/إنجليزي).
* **لوحة تحكم إدارية:** واجهة متكاملة (Django Admin) لإدارة كافة موارد النظام.

---

## 🛠️ التقنيات المستخدمة (Tech Stack)

* **Backend:** [Django 5.x](https://www.djangoproject.com/)
* **Database:** SQLite or PostgreSQL (Recommended) 
* **Frontend:** Django Templates + Bootstrap 5 + HTML + CSS +JavaScript
* **Production:** Gunicorn + Nginx + SSL

---

## ⚙️ إعدادات السيرفر (System Infrastructure)

تم إعداد النظام ليعمل خلف **Nginx** كموزع طلبات (Reverse Proxy) و **Gunicorn** كمشغل للتطبيق.

### 1. إعداد خادم الويب (Nginx)

يتم وضع الإعداد التالي في `/etc/nginx/sites-available/helpdesk`:

```nginx
# 1. تحويل حركة المرور من HTTP إلى HTTPS
server {
    listen 80;
    server_name 10.10.200.128; # أو الدومين المعتمد
    return 301 https://$host$request_uri;
}

# 2. إعداد سيرفر HTTPS الأساسي
server {
    listen 443 ssl;
    server_name 10.10.200.128;

    ssl_certificate /etc/ssl/certs/nginx-selfsigned.crt;
    ssl_certificate_key /etc/ssl/private/nginx-selfsigned.key;

    # رؤوس الأمان (Security Headers)
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    location /static/ { alias /var/www/helpdesk_system/staticfiles/; }
    location /media/ { alias /var/www/helpdesk_system/media/; }

    location / {
        proxy_pass http://unix:/run/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_redirect off;
    }
}

```

> **تنبيه:** تم رفع قيم `proxy_headers_hash` في ملف `nginx.conf` الأساسي لضمان استقرار الربط مع Azure.

### 2. إعداد مشغل التطبيق (Gunicorn Service)

يتم إنشاء ملف الخدمة في `/etc/systemd/system/gunicorn.service`:

```ini
[Unit]
Description=gunicorn daemon for helpdesk_system
After=network.target

[Service]
User=aloola
Group=www-data
WorkingDirectory=/var/www/helpdesk_system
ExecStart=/var/www/helpdesk_system/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/run/gunicorn.sock \
    helpdesk_system.wsgi:application

[Install]
WantedBy=multi-user.target

```

---

## 🚀 التثبيت والتشغيل (Installation)

1. **إعداد البيئة:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

```


2. **توليد مفتاح الأمان (Secret Key):**
قم بتشغيل الأمر التالي وانسخ الناتج إلى خانة `SECRET_KEY` في ملف `.env`:
```bash
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

```


3. **تهيئة قاعدة البيانات:**
```bash
python manage.py migrate
python manage.py loaddata groups.json
python manage.py collectstatic --noinput

```



---

## 🔐 الأمان و .env

يحتوي ملف `.env` (الذي يتم تسليمه منفصلاً) على المتغيرات الحساسة. **يمنع منعاً باتاً رفعه على GitHub**. يتضمن الملف:

* `SECRET_KEY`: مفتاح التشفير الخاص بالتطبيق.
* `MICROSOFT_CLIENT_ID` & `SECRET`: بيانات الربط مع Microsoft Azure.
* `DATABASE_URL`: بيانات الاتصال بقاعدة البيانات.

---

## 🛠️ الأوامر الحيوية وسجلات العمل (Maintenance & Logs)

* **إعادة تشغيل النظام:** `sudo systemctl restart gunicorn && sudo systemctl restart nginx`
* **مراقبة أداء التطبيق (Logs):**
`sudo journalctl -u gunicorn -f`
* **مراقبة أخطاء الويب:**
`sudo tail -f /var/log/nginx/error.log`

---

**حقوق التطوير © 2026**

---
