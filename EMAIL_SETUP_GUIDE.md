# حل مشكلة حظر Gmail للرسائل الإلكترونية

## المشكلة
يحظر Gmail الرسائل المرسلة من حسابات شخصية إلى عناوين الجامعات والطلاب، مما يؤدي إلى رفض الرسائل مع رسالة: "لا يرسل الى امايل استاد و تلميذ"

## الحلول المتاحة

### الحل 1: استخدام بريد إلكتروني جامعي (الأفضل)
1. أنشئ ملف `.env` في نفس مجلد المشروع
2. أضف الإعدادات التالية:

```
EMAIL_HOST=smtp.university.edu
EMAIL_PORT=587
EMAIL_USER=interstellar.club@university.edu
EMAIL_PASS=your_university_email_password
EMAIL_FROM=interstellar.club@university.edu
```

**ملاحظة:** استبدل `university.edu` بنطاق الجامعة الفعلي (مثل: `univ-maroc.ma`)

### الحل 2: استخدام Gmail مع App Password
إذا لم يكن لديك بريد جامعي:

1. اذهب إلى: https://myaccount.google.com/apppasswords
2. أنشئ App Password جديد للتطبيق
3. أنشئ ملف `.env`:

```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your_university_gmail@gmail.com
EMAIL_PASS=your_16_character_app_password
EMAIL_FROM=interstellar.club@university.edu
```

**تحذير:** قد يستمر Gmail في حظر هذه الرسائل

### الحل 3: استخدام خدمة بريد إلكتروني احترافية

#### SendGrid (مجاني لـ 100 رسالة يومياً):
1. سجل في: https://sendgrid.com
2. أنشئ API Key
3. أضف إلى `.env`:

```
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USER=apikey
EMAIL_PASS=your_sendgrid_api_key
EMAIL_FROM=interstellar.club@university.edu
```

#### Mailgun (مجاني لـ 5000 رسالة شهرياً):
1. سجل في: https://www.mailgun.com
2. أنشئ domain مخصص
3. أضف إلى `.env`:

```
EMAIL_HOST=smtp.mailgun.org
EMAIL_PORT=587
EMAIL_USER=postmaster@your_domain.mailgun.org
EMAIL_PASS=your_mailgun_password
EMAIL_FROM=interstellar.club@your_domain.com
```

## كيفية إنشاء ملف .env

1. افتح محرر النصوص (مثل Notepad++)
2. انسخ أحد التكوينات أعلاه
3. احفظ الملف باسم `.env` في مجلد المشروع
4. أعد تشغيل الخادم

## اختبار الإعداد

شغل ملف `test_email.py` للاختبار:

```bash
python test_email.py
```

## نصائح إضافية

1. **لا تستخدم Gmail الشخصي** للجامعات - سيتم حظره
2. **استخدم دومين جامعي** إن أمكن
3. **خدمات البريد الاحترافية** أكثر موثوقية
4. **تحقق من السجلات** في وحدة التحكم لمعرفة حالة الإرسال

## استكشاف الأخطاء

### إذا ظهرت رسالة "Authentication failed":
- تأكد من صحة كلمة المرور
- لـ Gmail: استخدم App Password وليس كلمة المرور العادية

### إذا ظهرت رسالة "Connection failed":
- تحقق من اتصال الإنترنت
- تأكد من صحة إعدادات SMTP

### إذا ظهرت رسالة "Blocked":
- غير طريقة الإرسال (استخدم بريد جامعي أو خدمة احترافية)
