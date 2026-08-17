# -*- coding: utf-8 -*-
"""
Yangiliklar manbalari (RSS) va mavzu bo'yicha filtr kalit so'zlari.

MUHIM: RSS manzillar vaqt o'tishi bilan o'zgarishi yoki ba'zilari
vaqtincha ishlamay qolishi mumkin. Skript har bir manbani alohida
try/except bilan o'qiydi — biri ishlamasa, qolganlari ishlashda
davom etadi. Agar biror manba doim xato bersa, shu ro'yxatdan
manzilini yangilang yoki o'chirib tashlang.

Yangi manba qo'shish uchun shunchaki quyidagi ro'yxatga bitta
qator qo'shsangiz kifoya.
"""

SOURCES = [
    # --- Top biznes-maktablar ---
    {"name": "Harvard Business School — Working Knowledge", "rss": "https://hbswk.hbs.edu/rss.xml", "category": "business_school"},
    {"name": "Stanford Graduate School of Business — Insights", "rss": "https://www.gsb.stanford.edu/insights/rss.xml", "category": "business_school"},
    {"name": "MIT Sloan Management Review", "rss": "https://sloanreview.mit.edu/feed/", "category": "business_school"},
    {"name": "Knowledge at Wharton", "rss": "https://knowledge.wharton.upenn.edu/feed/", "category": "business_school"},
    {"name": "Yale Insights", "rss": "https://insights.som.yale.edu/rss.xml", "category": "business_school"},
    {"name": "Columbia Business School — Ideas at Work", "rss": "https://businessinsights.bloomberg.com/feed/", "category": "business_school"},
    {"name": "INSEAD Knowledge", "rss": "https://knowledge.insead.edu/rss.xml", "category": "business_school"},
    {"name": "Kellogg Insight (Northwestern)", "rss": "https://insight.kellogg.northwestern.edu/rss", "category": "business_school"},
    {"name": "Chicago Booth Review", "rss": "https://www.chicagobooth.edu/review/rss.xml", "category": "business_school"},
    {"name": "London Business School — Think", "rss": "https://www.london.edu/think/rss", "category": "business_school"},
    {"name": "Rotman Insights Hub (Toronto)", "rss": "https://www.rotman.utoronto.ca/insightshub/rss", "category": "business_school"},
    {"name": "Cambridge Judge Business School — Insight", "rss": "https://www.jbs.cam.ac.uk/insight/feed/", "category": "business_school"},
    {"name": "Oxford Saïd Business School", "rss": "https://www.sbs.ox.ac.uk/rss.xml", "category": "business_school"},
    {"name": "Darden Ideas to Action (Virginia)", "rss": "https://ideas.darden.virginia.edu/rss.xml", "category": "business_school"},

    # --- Mashhur biznes jurnallari / tadqiqot nashrlari ---
    {"name": "Harvard Business Review", "rss": "https://hbr.org/feed", "category": "magazine"},
    {"name": "McKinsey & Company", "rss": "https://www.mckinsey.com/insights/rss", "category": "magazine"},
    {"name": "Fast Company — Leadership", "rss": "https://www.fastcompany.com/leadership/rss", "category": "magazine"},
    {"name": "Forbes — Leadership", "rss": "https://www.forbes.com/leadership/feed/", "category": "magazine"},
    {"name": "Inc.com", "rss": "https://www.inc.com/rss.xml", "category": "magazine"},
    {"name": "Entrepreneur", "rss": "https://www.entrepreneur.com/latest.rss", "category": "magazine"},
    {"name": "Fortune — Leadership", "rss": "https://fortune.com/feed/", "category": "magazine"},

    # --- Psixologiya sahifalari ---
    {"name": "Psychology Today", "rss": "https://www.psychologytoday.com/us/rss.xml", "category": "psychology"},
    {"name": "APA — American Psychological Association", "rss": "https://www.apa.org/news/rss/apa-news.rss", "category": "psychology"},
    {"name": "Greater Good Magazine (Berkeley)", "rss": "https://greatergood.berkeley.edu/feeds/all", "category": "psychology"},
    {"name": "Behavioral Scientist", "rss": "https://behavioralscientist.org/feed/", "category": "psychology"},
    {"name": "Big Think", "rss": "https://bigthink.com/feed/", "category": "psychology"},
    {"name": "Verywell Mind", "rss": "https://www.verywellmind.com/feed", "category": "psychology"},
    {"name": "Mindful.org", "rss": "https://www.mindful.org/feed/", "category": "psychology"},
]

# Mavzu bo'yicha filtr — sarlavha/tavsifda shu so'zlardan biri
# uchrasa, maqola nomzod sifatida ko'rib chiqiladi.
KEYWORDS = [
    "leadership", "management", "self-management", "self-discipline",
    "discipline", "motivation", "time management", "procrastination",
    "willpower", "self-control", "habit", "habits", "productivity",
    "ego", "emotional intelligence", "decision making", "burnout",
    "focus", "goal setting", "team management", "employee engagement",
    "mindset", "resilience", "accountability", "delegation",
    "people management", "workplace psychology", "personal development",
]
