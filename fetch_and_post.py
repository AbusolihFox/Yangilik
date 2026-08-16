# -*- coding: utf-8 -*-
"""
Har kuni ishga tushadigan asosiy skript:
1. sources.py dagi barcha RSS manbalarni o'qiydi (agar manba doim
   yomon baholansa, uni avtomatik chetlab o'tadi — pastga qarang)
2. Mavzu bo'yicha (KEYWORDS) mos maqolalarni tanlaydi
3. Oldin ko'rilmagan (seen_urls) va oxirgi 365 kun ichidagilarni oladi
4. Har biriga ball beradi: yangilik (recency) + manba reytingi + mavzu reytingi
5. Agar sobit (RSS) manbalardan yetarli/sifatli nomzod topilmasa —
   Claude'ning veb-qidiruv vositasi orqali internetdan YANGI mos
   manba/maqolalarni o'zi qidirib topadi (disfavored manbalarni
   chetlab o'tishga urinadi)
6. Eng yaxshi 1 tasini tanlaydi
7. Claude API orqali o'zbek tilida sarlavha + 100-150 so'zlik xulosa yozadi
8. Telegramga 👍/👎 tugmalari bilan yuboradi
9. state.json ni yangilaydi
"""

import os
import sys
import json
import hashlib
import requests
import feedparser
from datetime import datetime, timezone
from time import mktime

from sources import SOURCES, KEYWORDS
from state_store import load_state, save_state, prune_old_seen

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
MAX_AGE_DAYS = 365
TOP_N = 1

# Manba bali shu chegaradan past tushsa (ketma-ket 👎), o'sha manba
# endi RSS orqali tekshirilmaydi va Claude'ga "bunga o'xshamagan,
# yangi manba top" deb aytiladi.
DISFAVOR_THRESHOLD = -3


def short_id(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:10]


def matched_keywords(text: str):
    text_low = text.lower()
    return [kw for kw in KEYWORDS if kw in text_low]


def entry_datetime(entry):
    for field in ("published_parsed", "updated_parsed"):
        val = getattr(entry, field, None)
        if val:
            return datetime.fromtimestamp(mktime(val), tz=timezone.utc)
    return datetime.now(timezone.utc)


def disfavored_source_names(state):
    return {
        name for name, score in state["source_scores"].items()
        if score <= DISFAVOR_THRESHOLD
    }


def collect_candidates(state):
    now = datetime.now(timezone.utc)
    candidates = []
    disfavored = disfavored_source_names(state)

    for src in SOURCES:
        if src["name"] in disfavored:
            print(f"[O'TKAZIB YUBORILDI] {src['name']} — doim yomon baholangan, endi tekshirilmaydi")
            continue
        try:
            feed = feedparser.parse(src["rss"])
        except Exception as e:
            print(f"[OGOHLANTIRISH] {src['name']} o'qib bo'lmadi: {e}")
            continue

        for entry in getattr(feed, "entries", []):
            url = getattr(entry, "link", None)
            if not url:
                continue
            if url in state["seen_urls"]:
                continue  # avval ko'rsatilgan

            pub_dt = entry_datetime(entry)
            age_days = (now - pub_dt).days
            if age_days > MAX_AGE_DAYS or age_days < 0:
                continue

            title = getattr(entry, "title", "")
            summary = getattr(entry, "summary", "") or getattr(entry, "description", "")
            full_text = f"{title} {summary}"

            topics = matched_keywords(full_text)
            if not topics:
                continue  # mavzuga mos kelmadi

            # --- ball hisoblash ---
            recency_score = max(0, (MAX_AGE_DAYS - age_days)) / MAX_AGE_DAYS * 10  # 0..10, yangi bo'lsa yuqori
            source_score = state["source_scores"].get(src["name"], 0)
            topic_score = sum(state["topic_scores"].get(t, 0) for t in topics)
            total_score = recency_score + source_score + topic_score

            candidates.append({
                "url": url,
                "title": title,
                "summary_raw": summary,
                "source": src["name"],
                "topics": topics,
                "date": pub_dt.isoformat(),
                "score": total_score,
            })

    candidates.sort(key=lambda c: c["score"], reverse=True)
    return candidates


def pick_top(candidates, n=TOP_N):
    """Iloji boricha har xil manbalardan tanlashga harakat qiladi."""
    chosen = []
    used_sources = set()
    for c in candidates:
        if len(chosen) >= n:
            break
        if c["source"] in used_sources and len(candidates) > n:
            continue
        chosen.append(c)
        used_sources.add(c["source"])
    # agar manba xilma-xilligi tufayli n taga yetmasa, qolganidan to'ldiramiz
    if len(chosen) < n:
        for c in candidates:
            if len(chosen) >= n:
                break
            if c not in chosen:
                chosen.append(c)
    return chosen


def discover_new_candidates(state, existing_candidates_count):
    """
    Sobit RSS ro'yxatidan yetarli/sifatli maqola topilmasa (yoki
    yaxshi manbalar tugab qolsa), Claude'ning veb-qidiruv vositasi
    orqali internetdan real vaqtda YANGI, hali sinab ko'rilmagan
    manba va maqolalarni izlaydi. Doim yomon baholangan manbalarni
    aytib, ulardan qochishni so'raydi.
    """
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    disfavored = sorted(disfavored_source_names(state))
    avoid_text = ", ".join(disfavored) if disfavored else "(hozircha yo'q)"

    known_sources = ", ".join(s["name"] for s in SOURCES)

    prompt = f"""Sen tadqiqot-yangiliklar agentisan. Internetdan qidiruv vositasi
orqali quyidagi mavzularda so'nggi 365 kun ichida chop etilgan, ishonchli
manbalardan (universitetlar, biznes-maktablar, tan olingan tadqiqot
nashrlari, psixologiya sahifalari) 3-5 ta maqola top:

Mavzular: odamlarni boshqarish (people management), liderlik, o'z-o'zini
boshqarish, motivatsiya, intizom (discipline), time management, ego,
irodani boshqarish (willpower/self-control), his-hayajonli intellekt,
qaror qabul qilish, ish joyidagi psixologiya, shaxsiy rivojlanish.

Talablar:
- Manbalar ishonchli va tan olingan bo'lishi kerak (masalan
  universitet sahifalari, yirik biznes nashrlari, ilmiy-psixologik
  jurnallar/sahifalar) — shaxsiy bloglar yoki tekshirilmagan saytlar EMAS.
- Quyidagi manbalardan QOCH (bular allaqachon doim yomon baholangan):
  {avoid_text}
- Quyidagi manbalar allaqachon muntazam tekshiriladi, ularni TAKRORLAMA,
  faqat ULARGA O'XSHASH lekin YANGI manbalarni top:
  {known_sources}
- Har bir natija uchun aniq, ishlaydigan URL bo'lishi shart.

Javobni FAQAT quyidagi JSON massiv formatida qaytar, boshqa hech qanday
matn, izoh yoki markdown belgilarisiz:

[
  {{"title": "...", "url": "https://...", "source_name": "...", "published_date": "YYYY-MM-DD yoki noaniq bo'lsa bo'sh", "snippet": "qisqa inglizcha tavsif"}}
]"""

    try:
        resp = client.messages.create(
