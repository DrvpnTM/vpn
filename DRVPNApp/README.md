# Dr VPN (دکتر وی پی ان)

<div dir="rtl">

**Dr VPN** یک برنامه ساده و متن‌باز وی پی ان برای اندروید است، با ظاهری شبیه Hiddify:
یک دکمه بزرگ برای اتصال، کارت اشتراک فعال و کارت سرور انتخاب‌شده.

- 🌐 سایت: [drvpn.net](https://drvpn.net/)
- 📄 مقاله: [راهنمای خرید اشتراک وی پی ان و معرفی Dr VPN](ARTICLE-fa.md)

## ✨ امکانات

- اتصال با یک ضربه روی دکمه بزرگ صفحه اصلی
- پشتیبانی از پروتکل‌های VLESS، VMess، Trojan، Shadowsocks، Hysteria2، WireGuard، SOCKS و HTTP
- افزودن اشتراک یا کانفیگ از لینک، کلیپ‌بورد، QR کد یا فایل
- به‌روزرسانی اشتراک با یک دکمه
- تست پینگ سرورها و مرتب‌سازی بر اساس سرعت
- پروکسی جداگانه برای هر برنامه (Per-App Proxy) و قوانین مسیریابی
- پشتیبانی از فارسی و حالت تیره

## 📥 دانلود

فایل APK با هر تغییر به‌صورت خودکار روی GitHub Actions ساخته می‌شود:
به تب **Actions** این مخزن بروید ← workflow به نام **Build Dr VPN APK** ← آخرین اجرای موفق ← بخش **Artifacts** ← فایل `DrVPN-universal` را دانلود کنید.

> نسخه فعلی یک نسخه آزمایشی (debug) است.

## 📱 نحوه استفاده

1. برنامه را نصب و باز کنید.
2. در بالای صفحه روی دکمه **+** بزنید و لینک اشتراک یا کانفیگ خود را از کلیپ‌بورد یا QR کد وارد کنید.
3. در تب **سرورها** سرور دلخواه را انتخاب کنید.
4. به تب **خانه** برگردید و روی دکمه بزرگ اتصال بزنید.

## 🛠 ساخت از سورس

```bash
# نیازمندی‌ها: JDK 21، Android SDK (platform 37)، Android NDK 29
export NDK_HOME=/path/to/android-ndk
bash compile-hevtun.sh && cp -r libs V2rayNG/app/
curl -fsSL -o V2rayNG/app/libs/libv2ray.aar \
  https://github.com/2dust/AndroidLibXrayLite/releases/download/v26.9.9/libv2ray.aar
cd V2rayNG && ./gradlew assemblePlaystoreDebug
```

## 📜 مجوز و تشکر

این برنامه متن‌باز و تحت مجوز **GPL-3.0** است (فایل [LICENSE](LICENSE)).
Dr VPN بر پایه پروژه متن‌باز [v2rayNG](https://github.com/2dust/v2rayNG) ساخته شده و از
[Xray-core](https://github.com/XTLS/Xray-core) و [hev-socks5-tunnel](https://github.com/heiher/hev-socks5-tunnel) استفاده می‌کند.
از سازندگان این پروژه‌ها سپاسگزاریم.

</div>
