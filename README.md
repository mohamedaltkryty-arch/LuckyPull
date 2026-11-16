# Lucky Pull — اسحب وفز

مشروع لعبة عربية RTL مبني باستخدام Godot 4.3، ومهيأ لهواتف Android.

## بناء APK تلقائياً

- كل دفع إلى فرع `main` يشغّل GitHub Actions.
- يمكن تشغيل البناء يدوياً من تبويب **Actions** عبر **Build Lucky Pull Android APK**.
- عند نجاح البناء يظهر artifact باسم `LuckyPull-v0.3.0-Android-Debug-APK` ويحتوي على `LuckyPull-Android.apk`.

الـAPK الناتج نسخة Debug للاختبار والتثبيت، ويوقّع بمفتاح مؤقت ينشأ داخل عملية البناء. لا تستخدمه كتحديث فوق إصدار موقّع بمفتاح مختلف، وليس إصدار Release للنشر العام.

## بنية الملفات

- `project-payload/LuckyPull_Godot4_v0.3.0.tar.gz.b64`: أجزاء أرشيف المشروع المصدر المضغوط.
- `.github/workflows/android-apk.yml`: مسار البناء والتحقق ورفع APK كـArtifact.

## مواصفات بناء Android

- Godot 4.3 القياسي مع قوالب التصدير المطابقة.
- اتجاه عمودي وتصميم عربي RTL.
- ARMv7 وARM64.
- لا يطلب التطبيق إذن الإنترنت.
- لا يتضمن مقامرة أو جوائز نقدية.

يتم فك الأرشيف داخل عامل GitHub Actions، واستيراد المشروع، ثم تصدير APK والتحقق من سلامة ملفه وتوقيعه قبل رفعه.


## Version 0.3.0 — Neon Cosmos

- New colorful cosmic visual identity and reworked Arabic RTL mobile screens.
- New Lucky Pull app icon and Android launcher icon.
- New animated pull interaction, custom reward dialog, refreshed cards, missions and chest screens.
