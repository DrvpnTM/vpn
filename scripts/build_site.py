#!/usr/bin/env python3
"""ساخت سایت چندزبانه GitHub Pages (پوشه docs) برای سئو."""
import html
import json
import os

BASE = "https://drvpntm.github.io/vpn/"
RAW = "https://raw.githubusercontent.com/DrvpnTM/vpn/HEAD/"
SUBS = [("All", "sub.txt"), ("Base64", "sub_base64.txt"), ("VLESS", "subs/vless.txt"),
        ("VMess", "subs/vmess.txt"), ("Trojan", "subs/trojan.txt"), ("Shadowsocks", "subs/ss.txt"),
        ("Hysteria2", "subs/hysteria2.txt"), ("Cloudflare", "subs/cloudflare.txt"),
        ("JSON (bots)", "subscriptions.json")]

L = {
 "fa": dict(path="", dir="rtl", name="فارسی",
   title="اشتراک رایگان وی پی ان | فیلترشکن رایگان و کانفیگ V2Ray رایگان — drvpn.net",
   desc="دریافت اشتراک رایگان فیلترشکن و وی پی ان؛ لینک ساب رایگان V2Ray، VLESS، VMess، Trojan و Hysteria2 برای Hiddify و v2rayNG. بدون خرید فیلترشکن، هر ۶۰ دقیقه به‌روز می‌شود.",
   h1="اشتراک رایگان وی پی ان", intro="لینک اشتراک رایگان فیلترشکن برای ایران و همه کشورها. بدون ثبت‌نام و بدون نیاز به خرید فیلترشکن؛ سرورها هر ۶۰ دقیقه تست و به‌روز می‌شوند.",
   links="لینک‌های اشتراک", copy="کپی", copied="کپی شد", updated="آخرین به‌روزرسانی", configs="کانفیگ",
   how="آموزش استفاده", steps=["لینک اشتراک را کپی کنید.", "در Hiddify یا v2rayNG گزینه افزودن اشتراک از کلیپ‌بورد را بزنید.", "حالت کمترین پینگ را انتخاب کنید و وصل شوید."],
   bots="برای ربات‌ها و ابزارهای کانفیگ‌یاب", bots_text="همه لینک‌ها در فایل JSON ماشین‌خوان هستند و بدون کلید API قابل استفاده‌اند.",
   faq=[("آیا این اشتراک وی پی ان رایگان است؟", "بله، کاملاً رایگان است و نیازی به خرید فیلترشکن نیست."),
        ("کانفیگ‌ها چند وقت یک‌بار به‌روز می‌شوند؟", "هر ۶۰ دقیقه به‌صورت خودکار.")],
   warn="این کانفیگ‌ها عمومی هستند؛ برای کارهای بانکی و حساس استفاده نکنید.",
   kw="اشتراک رایگان وی پی ان, فیلترشکن رایگان, وی پی ان رایگان, خرید فیلترشکن, کانفیگ رایگان v2ray, لینک ساب رایگان, هیدیفای"),
 "zh-CN": dict(path="zh/", dir="ltr", name="中文",
   title="免费VPN订阅 | 免费V2Ray节点 | 免费翻墙 — drvpn.net",
   desc="免费VPN订阅链接：免费 V2Ray、VLESS、VMess、Trojan、Hysteria2 节点，支持 Hiddify、v2rayNG、Clash Meta。无需购买VPN，每 60 分钟更新。",
   h1="免费VPN订阅", intro="免费科学上网订阅链接，无需注册、无需购买VPN。节点每 60 分钟测试并更新。",
   links="订阅链接", copy="复制", copied="已复制", updated="最后更新", configs="个节点",
   how="使用教程", steps=["复制订阅链接。", "在 Hiddify 或 v2rayNG 中从剪贴板导入订阅。", "选择延迟最低的节点并连接。"],
   bots="供机器人和节点收集工具使用", bots_text="所有链接都在机器可读的 JSON 文件中，无需 API 密钥。",
   faq=[("这个VPN订阅是免费的吗？", "是的，完全免费，无需购买VPN。"), ("多久更新一次？", "每 60 分钟自动更新。")],
   warn="这些是公开的免费节点，请勿用于网银等敏感操作。",
   kw="免费VPN订阅, 免费VPN, 免费节点, 免费翻墙, 免费机场, 科学上网, V2Ray免费订阅, 购买VPN"),
 "ar": dict(path="ar/", dir="rtl", name="العربية",
   title="اشتراك VPN مجاني | كونفيج V2Ray مجاني | كسر الحجب — drvpn.net",
   desc="احصل على اشتراك VPN مجاني: روابط V2Ray و VLESS و VMess و Trojan و Hysteria2 مجانية لتطبيق Hiddify و v2rayNG. بدون شراء VPN، تحديث كل 60 دقيقة.",
   h1="اشتراك VPN مجاني", intro="رابط اشتراك مجاني لكسر الحجب، بدون تسجيل وبدون شراء VPN. يتم اختبار الخوادم وتحديثها كل 60 دقيقة.",
   links="روابط الاشتراك", copy="نسخ", copied="تم النسخ", updated="آخر تحديث", configs="كونفيج",
   how="طريقة الاستخدام", steps=["انسخ رابط الاشتراك.", "في Hiddify أو v2rayNG أضف الاشتراك من الحافظة.", "اختر الخادم الأقل تأخيراً واتصل."],
   bots="للبوتات وأدوات جمع الكونفيجات", bots_text="جميع الروابط في ملف JSON قابل للقراءة آلياً وبدون مفتاح API.",
   faq=[("هل اشتراك VPN هذا مجاني؟", "نعم، مجاني بالكامل ولا حاجة لشراء VPN."), ("كم مرة يتم التحديث؟", "كل 60 دقيقة تلقائياً.")],
   warn="هذه خوادم عامة؛ لا تستخدمها للعمليات المصرفية أو الحساسة.",
   kw="اشتراك VPN مجاني, في بي ان مجاني, كسر الحجب, شراء VPN, كونفيج V2Ray مجاني"),
 "es": dict(path="es/", dir="ltr", name="Español",
   title="Suscripción VPN Gratis | Configs V2Ray Gratis — drvpn.net",
   desc="Obtén una suscripción VPN gratis: enlaces V2Ray, VLESS, VMess, Trojan y Hysteria2 gratuitos para Hiddify y v2rayNG. Sin comprar VPN, actualizado cada 60 minutos.",
   h1="Suscripción VPN gratis", intro="Enlaces de suscripción VPN gratis, sin registro y sin comprar VPN. Los servidores se prueban y actualizan cada 60 minutos.",
   links="Enlaces de suscripción", copy="Copiar", copied="Copiado", updated="Última actualización", configs="configs",
   how="Cómo usar", steps=["Copia el enlace de suscripción.", "En Hiddify o v2rayNG, añade la suscripción desde el portapapeles.", "Elige el servidor con menor ping y conéctate."],
   bots="Para bots y recolectores de configs", bots_text="Todos los enlaces están en un JSON legible por máquinas, sin clave API.",
   faq=[("¿Esta suscripción VPN es gratis?", "Sí, es totalmente gratis; no necesitas comprar una VPN."), ("¿Cada cuánto se actualiza?", "Cada 60 minutos automáticamente.")],
   warn="Son servidores públicos; no los uses para banca en línea ni operaciones sensibles.",
   kw="suscripción VPN gratis, VPN gratis, VPN gratuita, comprar VPN, config V2Ray gratis"),
 "ru": dict(path="ru/", dir="ltr", name="Русский",
   title="Бесплатная подписка VPN | Бесплатные конфиги V2Ray — drvpn.net",
   desc="Бесплатная подписка VPN: ссылки V2Ray, VLESS, VMess, Trojan и Hysteria2 для Hiddify и v2rayNG. Без покупки VPN, обновление каждые 60 минут.",
   h1="Бесплатная подписка VPN", intro="Бесплатные ссылки-подписки для обхода блокировок, без регистрации и покупки VPN. Серверы проверяются и обновляются каждые 60 минут.",
   links="Ссылки на подписку", copy="Копировать", copied="Скопировано", updated="Последнее обновление", configs="конфигов",
   how="Как пользоваться", steps=["Скопируйте ссылку-подписку.", "В Hiddify или v2rayNG добавьте подписку из буфера обмена.", "Выберите сервер с наименьшим пингом и подключитесь."],
   bots="Для ботов и сборщиков конфигов", bots_text="Все ссылки собраны в машиночитаемом JSON, без API-ключа.",
   faq=[("Эта подписка VPN бесплатная?", "Да, полностью бесплатная, покупать VPN не нужно."), ("Как часто обновляется?", "Каждые 60 минут автоматически.")],
   warn="Это публичные серверы; не используйте их для банковских операций.",
   kw="бесплатная подписка VPN, бесплатный VPN, купить VPN, обход блокировок, бесплатные конфиги V2Ray"),
 "hi": dict(path="hi/", dir="ltr", name="हिन्दी",
   title="मुफ्त VPN सब्सक्रिप्शन | फ्री V2Ray कॉन्फ़िग — drvpn.net",
   desc="मुफ्त VPN सब्सक्रिप्शन पाएँ: Hiddify और v2rayNG के लिए फ्री V2Ray, VLESS, VMess, Trojan और Hysteria2 लिंक। VPN खरीदने की ज़रूरत नहीं, हर 60 मिनट में अपडेट।",
   h1="मुफ्त VPN सब्सक्रिप्शन", intro="मुफ्त VPN सब्सक्रिप्शन लिंक, बिना रजिस्ट्रेशन और बिना VPN खरीदे। सर्वर हर 60 मिनट में टेस्ट और अपडेट होते हैं।",
   links="सब्सक्रिप्शन लिंक", copy="कॉपी", copied="कॉपी हो गया", updated="अंतिम अपडेट", configs="कॉन्फ़िग",
   how="उपयोग कैसे करें", steps=["सब्सक्रिप्शन लिंक कॉपी करें।", "Hiddify या v2rayNG में क्लिपबोर्ड से सब्सक्रिप्शन जोड़ें।", "सबसे कम पिंग वाला सर्वर चुनें और कनेक्ट करें।"],
   bots="बॉट और कॉन्फ़िग-फ़ाइंडर टूल के लिए", bots_text="सभी लिंक मशीन-पठनीय JSON फ़ाइल में हैं, API key की ज़रूरत नहीं।",
   faq=[("क्या यह VPN सब्सक्रिप्शन मुफ्त है?", "हाँ, पूरी तरह मुफ्त है; VPN खरीदने की ज़रूरत नहीं।"), ("कितनी बार अपडेट होता है?", "हर 60 मिनट में अपने आप।")],
   warn="ये सार्वजनिक सर्वर हैं; बैंकिंग के लिए इनका उपयोग न करें।",
   kw="मुफ्त VPN सब्सक्रिप्शन, फ्री VPN, मुफ्त VPN, VPN खरीदें, फ्री V2Ray कॉन्फ़िग"),
 "ms": dict(path="ms/", dir="ltr", name="Bahasa Melayu",
   title="Langganan VPN Percuma | Config V2Ray Percuma — drvpn.net",
   desc="Dapatkan langganan VPN percuma: pautan V2Ray, VLESS, VMess, Trojan dan Hysteria2 percuma untuk Hiddify dan v2rayNG. Tidak perlu beli VPN, dikemas kini setiap 60 minit.",
   h1="Langganan VPN percuma", intro="Pautan langganan VPN percuma, tanpa pendaftaran dan tanpa membeli VPN. Pelayan diuji dan dikemas kini setiap 60 minit.",
   links="Pautan langganan", copy="Salin", copied="Disalin", updated="Kemas kini terakhir", configs="config",
   how="Cara menggunakan", steps=["Salin pautan langganan.", "Dalam Hiddify atau v2rayNG, tambah langganan dari papan klip.", "Pilih pelayan dengan ping terendah dan sambung."],
   bots="Untuk bot dan alat pencari config", bots_text="Semua pautan dalam fail JSON yang boleh dibaca mesin, tanpa kunci API.",
   faq=[("Adakah langganan VPN ini percuma?", "Ya, percuma sepenuhnya; tidak perlu membeli VPN."), ("Berapa kerap dikemas kini?", "Setiap 60 minit secara automatik.")],
   warn="Ini pelayan awam; jangan gunakan untuk perbankan.",
   kw="langganan VPN percuma, VPN percuma, VPN free, beli VPN, config V2Ray percuma"),
 "my": dict(path="my/", dir="ltr", name="မြန်မာ",
   title="အခမဲ့ VPN Subscription | အခမဲ့ V2Ray Config — drvpn.net",
   desc="အခမဲ့ VPN subscription ရယူပါ- Hiddify နှင့် v2rayNG အတွက် အခမဲ့ V2Ray၊ VLESS၊ VMess၊ Trojan၊ Hysteria2 link များ။ VPN ဝယ်ရန်မလို၊ ၆၀ မိနစ်တိုင်း update။",
   h1="အခမဲ့ VPN Subscription", intro="အခမဲ့ VPN subscription link များ၊ စာရင်းသွင်းရန်မလို၊ VPN ဝယ်ရန်မလို။ ဆာဗာများကို ၆၀ မိနစ်တိုင်း စမ်းသပ်ပြီး update လုပ်သည်။",
   links="Subscription link များ", copy="Copy", copied="Copy ပြီး", updated="နောက်ဆုံး update", configs="config",
   how="အသုံးပြုနည်း", steps=["Subscription link ကို copy ကူးပါ။", "Hiddify သို့မဟုတ် v2rayNG တွင် clipboard မှ subscription ထည့်ပါ။", "Ping အနည်းဆုံး ဆာဗာကို ရွေးပြီး ချိတ်ဆက်ပါ။"],
   bots="Bot နှင့် config ရှာဖွေရေး tool များအတွက်", bots_text="Link အားလုံးကို JSON ဖိုင်တွင် ထည့်ထားပြီး API key မလိုပါ။",
   faq=[("ဤ VPN subscription သည် အခမဲ့လား?", "ဟုတ်ကဲ့၊ လုံးဝအခမဲ့ဖြစ်ပြီး VPN ဝယ်ရန်မလိုပါ။"), ("ဘယ်နှစ်ကြိမ် update လုပ်သလဲ?", "၆၀ မိနစ်တိုင်း အလိုအလျောက်။")],
   warn="ဤဆာဗာများသည် အများသုံးဖြစ်သည်၊ ဘဏ်လုပ်ငန်းအတွက် မသုံးပါနှင့်။",
   kw="အခမဲ့ VPN, အခမဲ့ VPN subscription, VPN ဝယ်ရန်, free VPN Myanmar, အခမဲ့ V2Ray config"),
}

CSS = """:root{--bg:#f7f8fa;--fg:#14161a;--muted:#5b6270;--card:#fff;--line:#e2e5ea;--accent:#0b6bcb}
@media (prefers-color-scheme:dark){:root{--bg:#0f1115;--fg:#e8eaee;--muted:#9aa2af;--card:#171a20;--line:#2a2f38;--accent:#5aa9ff}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.7 system-ui,-apple-system,"Segoe UI",Tahoma,sans-serif}
main{max-width:860px;margin:0 auto;padding:24px 16px 48px}nav{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:14px;margin-bottom:16px}
a{color:var(--accent)}h1{font-size:30px;margin:8px 0}h2{font-size:21px;margin-top:32px}.muted{color:var(--muted)}
.sub{display:flex;gap:8px;align-items:center;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 12px;margin:8px 0}
.sub b{min-width:110px;flex-shrink:0}.sub code{flex:1;min-width:0;overflow-x:auto;white-space:nowrap;font-size:13px;direction:ltr}
button{border:1px solid var(--line);background:var(--bg);color:var(--fg);border-radius:8px;padding:6px 12px;cursor:pointer;font:inherit;font-size:14px}
@media (max-width:560px){.sub{flex-wrap:wrap}.sub b{min-width:0;width:100%}}"""

JS = """const T=document.documentElement.dataset;document.querySelectorAll('button[data-u]').forEach(b=>b.onclick=()=>{navigator.clipboard.writeText(b.dataset.u).then(()=>{const o=b.textContent;b.textContent=T.copied;setTimeout(()=>b.textContent=o,1500)})});
fetch('%s').then(r=>r.json()).then(m=>{const e=document.getElementById('st');e.textContent=T.updated+': '+new Date(m.updated).toLocaleString()+' · '+m.total+' '+T.configs}).catch(()=>{});""" % (RAW + "subscriptions.json")


def page(code, d):
    e = html.escape
    alts = "\n".join(f'<link rel="alternate" hreflang="{c}" href="{BASE}{x["path"]}">' for c, x in L.items())
    alts += f'\n<link rel="alternate" hreflang="x-default" href="{BASE}">'
    nav = " ".join(f'<a href="{BASE}{x["path"]}" hreflang="{c}">{e(x["name"])}</a>' for c, x in L.items())
    subs = "\n".join(f'<div class="sub"><b>{e(n)}</b><code>{RAW}{f}</code><button data-u="{RAW}{f}">{e(d["copy"])}</button></div>' for n, f in SUBS)
    steps = "".join(f"<li>{e(s)}</li>" for s in d["steps"])
    faq = "".join(f"<h3>{e(q)}</h3><p>{e(a)}</p>" for q, a in d["faq"])
    ld = json.dumps([
        {"@context": "https://schema.org", "@type": "WebSite", "name": "drvpn.net", "url": BASE + d["path"], "inLanguage": code, "description": d["desc"]},
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in d["faq"]]},
    ], ensure_ascii=False)
    return f"""<!doctype html>
<html lang="{code}" dir="{d['dir']}" data-copied="{e(d['copied'])}" data-updated="{e(d['updated'])}" data-configs="{e(d['configs'])}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(d['title'])}</title>
<meta name="description" content="{e(d['desc'])}">
<meta name="keywords" content="{e(d['kw'])}, free vpn, free v2ray config, drvpn.net">
<meta name="robots" content="index,follow">
<link rel="canonical" href="{BASE}{d['path']}">
{alts}
<meta property="og:type" content="website">
<meta property="og:title" content="{e(d['title'])}">
<meta property="og:description" content="{e(d['desc'])}">
<meta property="og:url" content="{BASE}{d['path']}">
<meta name="twitter:card" content="summary">
<link rel="alternate" type="application/json" title="subscriptions" href="{RAW}subscriptions.json">
<script type="application/ld+json">{ld}</script>
<style>{CSS}</style>
</head>
<body>
<main>
<nav>{nav}</nav>
<h1>{e(d['h1'])}</h1>
<p>{e(d['intro'])}</p>
<p class="muted" id="st"></p>
<h2>{e(d['links'])}</h2>
{subs}
<h2>{e(d['how'])}</h2>
<ol>{steps}</ol>
<h2>{e(d['bots'])}</h2>
<p>{e(d['bots_text'])}</p>
<div class="sub"><b>JSON</b><code>{RAW}subscriptions.json</code><button data-u="{RAW}subscriptions.json">{e(d['copy'])}</button></div>
<h2>FAQ</h2>
{faq}
<p class="muted">⚠️ {e(d['warn'])}</p>
<p class="muted"><a href="https://github.com/DrvpnTM/vpn">GitHub</a> · drvpn.net</p>
</main>
<script>{JS}</script>
</body>
</html>
"""


def main():
    for code, d in L.items():
        os.makedirs(os.path.join("docs", d["path"]), exist_ok=True)
        with open(os.path.join("docs", d["path"], "index.html"), "w") as f:
            f.write(page(code, d))
    urls = "\n".join(
        f"  <url><loc>{BASE}{d['path']}</loc><changefreq>hourly</changefreq>"
        + "".join(f'<xhtml:link rel="alternate" hreflang="{c}" href="{BASE}{x["path"]}"/>' for c, x in L.items())
        + "</url>" for d in L.values())
    with open("docs/sitemap.xml", "w") as f:
        f.write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n{urls}\n</urlset>\n')
    with open("docs/robots.txt", "w") as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n")
    with open("docs/.nojekyll", "w") as f:
        pass


if __name__ == "__main__":
    main()
