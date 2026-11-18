# Lucky Pull — اسحب وفز

مشروع لعبة عربية RTL مبني باستخدام Godot 4.3، ومهيأ لهواتف Android.

## بناء APK تلقائياً

- كل دفع إلى فرع `main` يشغّل GitHub Actions.
- يمكن تشغيل البناء يدوياً من تبويب **Actions** عبر **Build Lucky Pull Android APK**.
- عند نجاح البناء يظهر artifact باسم `LuckyPull-v0.4.2-Android-Debug-APK` ويحتوي على `LuckyPull-Android.apk`.

الـAPK الناتج نسخة Debug للاختبار والتثبيت، ويوقّع بمفتاح مؤقت ينشأ داخل عملية البناء. لا تستخدمه كتحديث فوق إصدار موقّع بمفتاح مختلف، وليس إصدار Release للنشر العام.

## بنية الملفات

- `project-payload/LuckyPull_Godot4_v0.4.2.tar.gz.b64`: أجزاء أرشيف المشروع المصدر المضغوط.
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


## Version 0.4.2 — 14-Day Free Season

- Adds a recurring 14-day free season with 14 reward tiers and 1,400 season points.
- Season points are earned from successful pulls, chest openings, daily login gifts, and claimed daily missions.
- Rewards are claim-once, locally saved, and reset safely when the 14-day period expires.
- Adds an Arabic RTL / English LTR Season tab. The season has no paid pass, gambling, or cash prizes.
- Save schema migrates from v3 to v4 without discarding existing progress.


## Version 0.4.3 — Season Cadence Recovery

- Season rollover now catches up across all fully elapsed 14-day periods.
- The season schedule remains anchored to its original start timestamp, preventing drift when the game is not opened on expiry.
- Expired season points and unclaimed tier rewards are discarded; no rewards are granted for missed seasons.
- Automated tests cover three missed seasons, remaining duration, and the next scheduled rollover.
- Android version name/code updated to 0.4.3 / 8.
