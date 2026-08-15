# Universitet Yangiliklar Boti

Bu bot har kuni top universitetlar, biznes jurnallari va psixologiya
sahifalaridan biznes-menejment va shaxsiy rivojlanish (motivatsiya,
intizom, o'z-o'zini boshqarish, time management, ego va h.k.)
mavzusidagi eng mos 1 ta yangilikni tanlab, o'zbek tilida qisqa
xulosa bilan Telegramga yuboradi. Har bir xabar ostida 👍/👎 tugmalari
bor — ular orqali bot kelasi safar sizga qaysi manba/mavzular ko'proq
yoqishini "o'rganadi".

Hammasi **bepul** ishlaydi — GitHub Actions orqali, alohida server kerak emas.

---

## 1-qadam: Telegram bot yaratish

1. Telegramda **@BotFather** ni toping va yozing: `/newbot`
2. Botga nom va username bering (username `bot` bilan tugashi kerak,
   masalan `mening_universitet_botim`).
3. BotFather sizga bir qator **token** beradi, masalan:
   `123456789:AAExxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   — buni saqlab qo'ying, bu **TELEGRAM_BOT_TOKEN**.
4. Telegramda o'sha botingizni toping va unga istalgan xabar yozing
   (masalan "salom") — bot javob bermasa ham normal, faqat unga
   xabar yozganingiz kifoya.
5. Chat ID ni bilish uchun brauzerda quyidagi manzilni oching
   (TOKEN o'rniga o'z tokeningizni qo'ying):
   `https://api.telegram.org/botTOKEN/getUpdates`
   Natijada chiqqan JSON ichida `"chat":{"id":123456789...}` qismini
   toping — shu raqam sizning **TELEGRAM_CHAT_ID** bo'ladi.

## 2-qadam: Anthropic API kalitini olish

1. https://console.anthropic.com saytiga kiring, ro'yxatdan o'ting.
2. "API Keys" bo'limidan yangi kalit yarating — bu **ANTHROPIC_API_KEY**.
3. Hisobingizga ozgina pul (masalan $5) qo'shing — kunlik 1 ta
   xulosa yozish juda arzon (oyiga taxminan bir necha sent-dollar
   atrofida) turadi.

## 3-qadam: GitHub repository yaratish

1. https://github.com da yangi **public** repository yarating
   (masalan `uni-news-bot`). Public bo'lishi kerak — shunda GitHub
   Actions vaqti cheksiz bepul bo'ladi.
2. Ushbu papkadagi barcha fayllarni (README, .github papkasi bilan
   birga) shu repoga yuklang. Buning eng oson yo'li:
   - Kompyuteringizda: repo'ni clone qiling, fayllarni ichiga
     ko'chiring, `git add . && git commit -m "init" && git push`
   - Yoki GitHub veb-saytida "Add file → Upload files" orqali qo'lda
     yuklang (papka strukturasini saqlagan holda).

## 4-qadam: Maxfiy kalitlarni (Secrets) qo'shish

Repo ichida: **Settings → Secrets and variables → Actions → New repository secret**

Quyidagi 3 ta secret'ni qo'shing:

| Nomi | Qiymati |
|---|---|
| `TELEGRAM_BOT_TOKEN` | 1-qadamda olingan token |
| `TELEGRAM_CHAT_ID` | 1-qadamda topilgan chat ID |
| `ANTHROPIC_API_KEY` | 2-qadamda olingan kalit |

## 5-qadam: Ishga tushirish

Ikkita workflow avtomatik jadval bo'yicha ishlaydi:

- **Kunlik yangilik yuborish** — har kuni soat 08:00 (Toshkent vaqti)
- **Baholarni tekshirish** — har 15 daqiqada (tugma bosilganini tekshiradi)

Kutmasdan sinab ko'rish uchun: repo ichida **Actions** bo'limiga
kiring, "Kunlik yangilik yuborish" workflow'ini tanlang va
**"Run workflow"** tugmasini bosing — bir necha soniyada Telegramga
birinchi xabar kelishi kerak.

---

## Fayllar tuzilishi

```
sources.py            — RSS manbalar va kalit so'zlar ro'yxati
state_store.py         — "xotira" (state.json) bilan ishlash
fetch_and_post.py       — kunlik: yangilik topish, xulosa, yuborish
poll_feedback.py        — 👍/👎 tugmalarni tekshirish
state.json              — bot xotirasi (avtomatik yangilanadi, qo'l tegmasin)
requirements.txt         — kerakli Python kutubxonalari
.github/workflows/       — avtomatik ishga tushirish jadvali
```

## Manbalar qanday yangilanadi

`sources.py` dagi 14 ta manba — **boshlang'ich ro'yxat**, qat'iy emas:

- Agar biror manbaning umumiy bali ketma-ket 👎 tufayli **-3** ga
  tushib qolsa, bot o'sha manbani RSS orqali tekshirishni **avtomatik
  to'xtatadi**.
- Shunday holatda (yoki umuman yetarli mos maqola topilmasa) bot
  Claude'ning veb-qidiruv vositasi orqali **internetdan real vaqtda
  yangi, ishonchli manba/maqolalarni o'zi qidirib topadi** — bunda
  yomon baholangan manbalardan qochishga harakat qiladi.
- Bu qidiruv har kuni emas, faqat kerak bo'lganda (ishlaydigan
  manbalar yetishmasa) ishga tushadi — shuning uchun API xarajati
  sezilarli oshmaydi.
- Bunday topilgan manbalar doimiy ro'yxatga (`sources.py`) avtomatik
  yozilmaydi — har safar kerak bo'lganda qayta qidiriladi. Agar
  qandaydir yangi manba doimiy yoqsa, uni qo'lda `sources.py` ga
  qo'shib qo'yishingiz mumkin.

## Sozlash / o'zgartirish

- **Manbalar ro'yxati**: `sources.py` faylidagi `SOURCES` ro'yxatiga
  istalgan RSS manzilni qo'shishingiz yoki o'chirishingiz mumkin.
- **Mavzu kalit so'zlari**: `sources.py` dagi `KEYWORDS` ro'yxatini
  kengaytirishingiz mumkin (masalan yangi mavzu qo'shish uchun).
- **Kuniga nechta yangilik**: `fetch_and_post.py` faylida
  `TOP_N = 1` qatorini o'zgartiring.
- **Yuborish vaqti**: `.github/workflows/daily_post.yml` faylidagi
  `cron: "0 3 * * *"` qatorini o'zgartiring (vaqt UTC bo'yicha,
  Toshkent = UTC+5).

## Diqqat qiling

- Ba'zi RSS manzillar vaqt o'tishi bilan o'zgarishi mumkin — agar
  bironta manba doim xato bersa, Actions loglarida
  "[OGOHLANTIRISH] ... o'qib bo'lmadi" deb chiqadi, o'sha manbani
  `sources.py` da tekshiring/yangilang.
- GitHub public repolarda schedule'lar 60 kun davomida repoga hech
  qanday commit bo'lmasa avtomatik to'xtatiladi — lekin bu bot har
  kuni o'zi commit qilib turgani uchun bu muammo bo'lmaydi.
