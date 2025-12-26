@echo off
echo ============================================
echo رفع مشروع INTERSTELLAR CLUB إلى GitHub
echo ============================================
echo.

REM التحقق من وجود Git
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Git غير مثبت على النظام
    echo يرجى تحميل Git من: https://git-scm.com/downloads
    echo ثم تشغيل هذا الملف مرة أخرى
    pause
    exit /b 1
)

echo ✅ Git مثبت على النظام
echo.

REM إعداد Git (إذا لم يكن مهيأ مسبقاً)
echo أدخل اسم المستخدم الخاص بك على GitHub:
set /p github_username=
echo أدخل بريدك الإلكتروني المرتبط بحساب GitHub:
set /p github_email=

git config user.name "%github_username%"
git config user.email "%github_email%"

echo.
echo 🔧 تم إعداد Git بنجاح
echo.

REM إنشاء repository محلي
echo 📁 إعداد repository محلي...
git init

REM إضافة الملفات
echo 📤 إضافة الملفات...
git add .

REM التحقق من وجود ملفات حساسة
if exist ".env" (
    echo ⚠️  تم العثور على ملف .env - سيتم تجاهله
    git reset .env
)

REM إنشاء commit
echo 💾 إنشاء commit...
git commit -m "Initial commit - INTERSTELLAR CLUB application"

echo.
echo 🎯 الآن تحتاج إلى إنشاء repository على GitHub:
echo 1. اذهب إلى https://github.com/new
echo 2. أدخل اسم المشروع: interstellar-club
echo 3. اضغط "Create repository"
echo 4. انسخ رابط الـ repository
echo.
echo أدخل رابط الـ repository (يبدأ بـ https://github.com/):
set /p repo_url=

REM إضافة remote و push
echo 🔗 ربط المشروع بـ GitHub...
git remote add origin "%repo_url%"
git branch -M main
echo 📤 رفع الملفات إلى GitHub...
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ✅ تم رفع المشروع بنجاح إلى GitHub!
    echo.
    echo 🌐 رابط المشروع: %repo_url%
    echo.
    echo 📋 الخطوات التالية:
    echo 1. اذهب إلى https://heroku.com
    echo 2. أنشئ تطبيق جديد
    echo 3. اربط GitHub repository
    echo 4. فعل النشر التلقائي
    echo 5. اضف متغيرات البيئة
    echo.
    echo 🎉 تهانينا! موقعك سيعمل قريباً 24/7!
) else (
    echo.
    echo ❌ فشل في رفع المشروع
    echo تحقق من:
    echo - صحة رابط الـ repository
    echo - صلاحيات الدفع إلى GitHub
    echo - اتصال الإنترنت
)

echo.
pause
