# -*- coding: utf-8 -*-
"""
state.json bilan ishlash uchun yordamchi funksiyalar.
Bu fayl "botning xotirasi" — qaysi maqolalar ko'rsatilgan,
qaysi manba/mavzular ko'proq yoqadi (like) yoki yoqmaydi (dislike).
"""

import json
import os

STATE_PATH = os.path.join(os.path.dirname(__file__), "state.json")

DEFAULT_STATE = {
    "seen_urls": {},        # url -> {"date": "...", "source": "...", "topics": [...]}
    "source_scores": {},    # source_name -> int
    "topic_scores": {},     # keyword -> int
    "pending_feedback": {}, # short_id -> {"url":..., "source":..., "topics":[...], "chat_id":..., "message_id":...}
    "last_update_id": 0,    # Telegram getUpdates uchun offset
}


def load_state():
    if not os.path.exists(STATE_PATH):
        return json.loads(json.dumps(DEFAULT_STATE))
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    # eski state fayllarda yangi kalitlar bo'lmasligi mumkin
    for k, v in DEFAULT_STATE.items():
        data.setdefault(k, v)
    return data


def save_state(state):
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def prune_old_seen(state, max_days=365):
    """365 kundan eski yozuvlarni seen_urls dan tozalaydi (fayl shishib
    ketmasligi uchun) — lekin bu ularni QAYTA taklif qilinishiga olib
    kelishi mumkin, shuning uchun ehtiyotkorlik bilan ishlatiladi."""
    from datetime import datetime, timedelta
    cutoff = datetime.utcnow() - timedelta(days=max_days * 2)  # ikki barobar zaxira
    to_delete = []
    for url, info in state["seen_urls"].items():
        try:
            d = datetime.fromisoformat(info["date"])
            if d < cutoff:
                to_delete.append(url)
        except Exception:
            continue
    for url in to_delete:
        del state["seen_urls"][url]
