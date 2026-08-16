# -*- coding: utf-8 -*-
"""
Bu skript kuniga bir marta (kun oxirida) ishga tushib, Telegramda
foydalanuvchi bosgan 👍/👎 tugmalarni tekshiradi va kelasi safar
qanday yangilik tanlash kerakligini "o'rgatadi":

- 👍 bosilsa: shu maqolaning manbasi va mavzu-teglariga +1 ball
- 👎 bosilsa: -1 ball (shu manba/mavzudan kamroq maqola tanlanadi)
- Hech narsa BOSILMASA: bu ham "yoqdi" deb hisoblanadi (+1 ball) —
  chunki javob kutilayotgan xabar bir kun o'tgach avtomatik
  "yoqdi" deb yopiladi.

Telegramning o'zida "webhook server" saqlab turish shart emas —
getUpdates orqali oddiy so'rov (polling) yetarli.
"""

import os
import requests

from state_store import load_state, save_state

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


def answer_callback(callback_query_id, text):
    requests.post(
        f"{TELEGRAM_API}/answerCallbackQuery",
        json={"callback_query_id": callback_query_id, "text": text},
        timeout=15,
    )


def edit_message_markup(chat_id, message_id, result_text):
    requests.post(
        f"{TELEGRAM_API}/editMessageReplyMarkup",
        json={
            "chat_id": chat_id,
            "message_id": message_id,
            "reply_markup": {"inline_keyboard": [[{"text": result_text, "callback_data": "noop"}]]},
        },
        timeout=15,
    )


def apply_feedback(state, article_id, info, delta):
    state["source_scores"][info["source"]] = state["source_scores"].get(info["source"], 0) + delta
    for topic in info["topics"]:
        state["topic_scores"][topic] = state["topic_scores"].get(topic, 0) + delta
    del state["pending_feedback"][article_id]


def main():
    state = load_state()
    offset = state.get("last_update_id", 0)

    r = requests.get(
        f"{TELEGRAM_API}/getUpdates",
        params={"offset": offset + 1, "timeout": 0},
        timeout=30,
    )
    r.raise_for_status()
    updates = r.json().get("result", [])

    answered_ids = set()

    for update in updates:
        state["last_update_id"] = max(state["last_update_id"], update["update_id"])

        cq = update.get("callback_query")
        if not cq:
            continue

        data = cq.get("data", "")
        chat_id = cq["message"]["chat"]["id"]
        message_id = cq["message"]["message_id"]

        if "|" not in data:
            continue
        action, article_id = data.split("|", 1)

        info = state["pending_feedback"].get(article_id)
        if not info:
            # allaqachon baholangan yoki topilmadi
            answer_callback(cq["id"], "Bu allaqachon baholangan.")
            continue

        delta = 1 if action == "like" else -1 if action == "dislike" else 0

        apply_feedback(state, article_id, info, delta)
        answered_ids.add(article_id)

        result_label = "✅ Baholadingiz: Yaxshi" if delta > 0 else "✅ Baholadingiz: Yomon"
        answer_callback(cq["id"], "Rahmat! Kelasi tanlovlarga hisobga olamiz.")
        edit_message_markup(chat_id, message_id, result_label)

        print(f"Baho qabul qilindi: {action} -> {info['source']}")

    # Hali javob kutayotgan (bosilmagan) qolgan barcha xabarlar —
    # bir kun o'tgani uchun "yoqdi" deb hisoblanadi.
    remaining = list(state["pending_feedback"].items())
    for article_id, info in remaining:
        if article_id in answered_ids:
            continue
        message_id = info.get("message_id")
        apply_feedback(state, article_id, info, delta=1)
        if message_id:
            edit_message_markup(TELEGRAM_CHAT_ID, message_id, "✅ Baho berilmadi — yoqqan deb hisoblandi")
        print(f"Javobsiz qoldi, avtomatik 'yoqdi' deb hisoblandi -> {info['source']}")

    save_state(state)


if __name__ == "__main__":
    main()
