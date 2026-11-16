# Lucky Pull — اسحب وفز

مشروع لعبة عربية RTL مبني باستخدام Godot 4.3، ومهيأ لهواتف Android.

## بناء APK تلقائياً

- كل دفع إلى فرع `main` يشغّل GitHub Actions.
- يمكن تشغيل البناء يدوياً من تبويب **Actions** عبر **Build Lucky Pull Android APK**.
- عند نجاح البناء يظهر artifact باسم `LuckyPull-v0.3.4-Android-Debug-APK` ويحتوي على `LuckyPull-Android.apk`.

الـAPK الناتج نسخة Debug للاختبار والتثبيت، ويوقّع بمفتاح مؤقت ينشأ داخل عملية البناء. لا تستخدمه كتحديث فوق إصدار موقّع بمفتاح مختلف، وليس إصدار Release للنشر العام.

## بنية الملفات

- `project-payload/LuckyPull_Godot4_v0.3.4.tar.gz.b64`: أجزاء أرشيف المشروع المصدر المضغوط.
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


## Version 0.3.2 — Typography Refresh

- Complete text hierarchy refresh across all game screens.
- Embedded Arabic Regular, SemiBold, and Bold font weights.
- Larger small text, clearer button labels, and consistent line spacing.


## Version 0.3.3 — Save Recovery Protection

- Prevents an older build from overwriting a save created by a newer build.
- Recovers a corrupt primary save from a valid backup without replacing a future-version primary.
- Verifies temporary writes and backup rotation before promoting a new save.
- Shows an Arabic/English recovery warning and disables daily claims while recovery is read-only.
- Adds automated Godot smoke tests for save recovery, legacy migration, and probability totals.
- Synchronizes Android version metadata to 0.3.3 (version code 3).


## Version 0.3.4 — Save Parser & Test Cleanup

- Parses malformed save files without emitting an expected JSON parser error during backup recovery.
- Cleans up temporary state objects in the automated tests.
- Android version code is now 4.
