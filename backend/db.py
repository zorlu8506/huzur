"""
Kalıcı veri (SQLite, stdlib — ek kurulum yok).
- mood_log: günlük ruh hali takibi -> haftalık/aylık seyir grafiği
- feedback: (-1/0/+1) -> hangi içerik hangi duyguya iyi geliyor (optimizasyon)
- favorites: 'Şifa Koleksiyonum / Sığınak'
Basit tutuldu: tek kullanıcı (local). Çok kullanıcıda user_id kolonu eklenir.
"""
import sqlite3, pathlib, datetime, json, hashlib

DB = pathlib.Path(__file__).resolve().parent.parent / "data" / "sekine.db"


def _conn():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c


def init():
    with _conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS mood_log(
          id INTEGER PRIMARY KEY, ts TEXT, main TEXT, sub TEXT);
        CREATE TABLE IF NOT EXISTS feedback(
          id INTEGER PRIMARY KEY, ts TEXT, main TEXT, sub TEXT,
          layer TEXT, content_id TEXT, value INTEGER);
        CREATE TABLE IF NOT EXISTS favorites(
          id INTEGER PRIMARY KEY, ts TEXT, main TEXT, sub TEXT,
          layer TEXT, content_id TEXT, payload TEXT,
          UNIQUE(layer, content_id));
        CREATE TABLE IF NOT EXISTS visits(
          id INTEGER PRIMARY KEY, ts TEXT, day TEXT, path TEXT,
          visitor TEXT, ua TEXT, referrer TEXT, is_bot INTEGER DEFAULT 0);
        CREATE INDEX IF NOT EXISTS idx_visits_day ON visits(day);
        """)


def _now():
    return datetime.datetime.now().isoformat(timespec="seconds")


def log_mood(main, sub):
    with _conn() as c:
        c.execute("INSERT INTO mood_log(ts,main,sub) VALUES(?,?,?)", (_now(), main, sub))


def log_feedback(main, sub, cards, value):
    with _conn() as c:
        for card in cards:
            c.execute("INSERT INTO feedback(ts,main,sub,layer,content_id,value) VALUES(?,?,?,?,?,?)",
                      (_now(), main, sub, card.get("layer"), card.get("content_id"), value))


def add_favorite(main, sub, layer, content_id, payload):
    with _conn() as c:
        c.execute("""INSERT OR IGNORE INTO favorites(ts,main,sub,layer,content_id,payload)
                     VALUES(?,?,?,?,?,?)""",
                  (_now(), main, sub, layer, content_id, json.dumps(payload, ensure_ascii=False)))


def list_favorites():
    with _conn() as c:
        rows = c.execute("SELECT * FROM favorites ORDER BY id DESC").fetchall()
    return [{**dict(r), "payload": json.loads(r["payload"])} for r in rows]


def mood_summary(days=14):
    since = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat()
    with _conn() as c:
        rows = c.execute("""SELECT date(ts) d, main, COUNT(*) n
                            FROM mood_log WHERE ts >= ?
                            GROUP BY d, main ORDER BY d""", (since,)).fetchall()
        top = c.execute("""SELECT main, sub, COUNT(*) n FROM mood_log WHERE ts >= ?
                           GROUP BY main, sub ORDER BY n DESC LIMIT 1""", (since,)).fetchone()
    daily = {}
    for r in rows:
        daily.setdefault(r["d"], {})[r["main"]] = r["n"]
    hint = None
    if top:
        hint = (f"Son {days} günde en çok '{top['main']} · {top['sub']}' öne çıktı. "
                f"Bu hafta seninle bu temaya biraz daha ağırlık verelim mi?")
    return {"days": days, "daily": daily, "dominant": dict(top) if top else None, "hint": hint}


def best_content(main, sub, layer, limit=3):
    """Bu duygu+katman için geçmişte en çok +1 alan içerikler (kişiselleştirme)."""
    with _conn() as c:
        rows = c.execute("""SELECT content_id, SUM(value) score, COUNT(*) n
                            FROM feedback WHERE main=? AND sub=? AND layer=? AND content_id IS NOT NULL
                            GROUP BY content_id ORDER BY score DESC LIMIT ?""",
                         (main, sub, layer, limit)).fetchall()
    return [dict(r) for r in rows]


def mood_trend(days=14):
    """Grafik için gün gün duygu dağılımı + günlük 'huzur' (feedback ortalaması)."""
    today = datetime.date.today()
    dates = [(today - datetime.timedelta(days=i)) for i in range(days - 1, -1, -1)]
    since = (today - datetime.timedelta(days=days - 1)).isoformat()
    with _conn() as c:
        mrows = c.execute("""SELECT date(ts) d, main, COUNT(*) n FROM mood_log
                             WHERE date(ts) >= ? GROUP BY d, main""", (since,)).fetchall()
        frows = c.execute("""SELECT date(ts) d, AVG(value) avg, COUNT(*) n FROM feedback
                             WHERE date(ts) >= ? GROUP BY d""", (since,)).fetchall()
    by_day = {}
    for r in mrows:
        by_day.setdefault(r["d"], {})[r["main"]] = r["n"]
    huzur = {r["d"]: {"avg": round(r["avg"], 3), "n": r["n"]} for r in frows}
    totals = {}
    for r in mrows:
        totals[r["main"]] = totals.get(r["main"], 0) + r["n"]
    series = []
    for d in dates:
        ds = d.isoformat()
        series.append({
            "date": ds,
            "label": d.strftime("%d.%m"),
            "by_main": by_day.get(ds, {}),
            "entries": sum(by_day.get(ds, {}).values()),
            "huzur": huzur.get(ds, {}).get("avg"),
        })
    return {"days": days, "series": series, "totals": totals,
            "summary": mood_summary(days)}


# ============================ ZİYARET İSTATİSTİĞİ ============================
# Gizlilik: ham IP saklanmaz. Ziyaretçi kimliği = sha256(ip|ua|gün) ilk 16 hane
# (günlük rotasyon → tekil sayımı yapılır ama kişi izlenmez).
_BOT_UA = ("bot", "spider", "crawl", "slurp", "bing", "google", "yandex", "baidu",
           "duckduck", "facebookexternalhit", "whatsapp", "telegram", "headless",
           "preview", "monitor", "uptime", "curl", "wget", "python-requests", "go-http")


def _is_bot(ua):
    u = (ua or "").lower()
    return 1 if any(b in u for b in _BOT_UA) else 0


def _visitor_id(ip, ua):
    day = datetime.date.today().isoformat()
    return hashlib.sha256(f"{ip}|{ua}|{day}".encode()).hexdigest()[:16]


def _ref_host(ref):
    """Referrer'ı okunur kaynağa indir (host). Boş/kendi domaini → 'Doğrudan'."""
    if not ref:
        return "Doğrudan / kayıtsız"
    try:
        h = ref.split("//", 1)[-1].split("/", 1)[0].lower()
        if h.startswith("www."):
            h = h[4:]
        if "keshf" in h:
            return "Doğrudan / kayıtsız"
        return h or "Doğrudan / kayıtsız"
    except Exception:
        return "Doğrudan / kayıtsız"


def log_visit(path, ip, ua, referrer):
    with _conn() as c:
        c.execute("INSERT INTO visits(ts,day,path,visitor,ua,referrer,is_bot) VALUES(?,?,?,?,?,?,?)",
                  (_now(), datetime.date.today().isoformat(), (path or "/")[:120],
                   _visitor_id(ip, ua), (ua or "")[:300], (referrer or "")[:300], _is_bot(ua)))


def visit_stats(days=30, include_bots=False):
    today = datetime.date.today()
    dates = [(today - datetime.timedelta(days=i)) for i in range(days - 1, -1, -1)]
    since = dates[0].isoformat()
    bf = "" if include_bots else "AND is_bot=0"

    def _rng(n):
        s = (today - datetime.timedelta(days=n - 1)).isoformat()
        with _conn() as c:
            r = c.execute(f"SELECT COUNT(*) v, COUNT(DISTINCT visitor) u FROM visits "
                          f"WHERE day>=? {bf}", (s,)).fetchone()
        return {"visits": r["v"] or 0, "uniq": r["u"] or 0}

    with _conn() as c:
        drows = c.execute(f"""SELECT day, COUNT(*) visits, COUNT(DISTINCT visitor) uniq
                              FROM visits WHERE day>=? {bf} GROUP BY day""", (since,)).fetchall()
        total = c.execute(f"SELECT COUNT(*) v, COUNT(DISTINCT visitor) u FROM visits "
                          f"WHERE 1=1 {bf}").fetchone()
        refs = c.execute(f"""SELECT referrer, COUNT(*) n FROM visits
                             WHERE day>=? {bf} GROUP BY referrer""", (since,)).fetchall()
        uarows = c.execute(f"SELECT ua FROM visits WHERE day>=? {bf}", (since,)).fetchall()
        botcnt = c.execute("SELECT COUNT(*) n FROM visits WHERE day>=? AND is_bot=1",
                           (since,)).fetchone()["n"]

    by_day = {r["day"]: {"visits": r["visits"], "uniq": r["uniq"]} for r in drows}
    series = [{"date": d.isoformat(), "label": d.strftime("%d.%m"),
               "visits": by_day.get(d.isoformat(), {}).get("visits", 0),
               "uniq": by_day.get(d.isoformat(), {}).get("uniq", 0)} for d in dates]

    # referrer'ları host bazında topla
    ref_agg = {}
    for r in refs:
        host = _ref_host(r["referrer"])
        ref_agg[host] = ref_agg.get(host, 0) + r["n"]
    referrers = sorted([{"kaynak": k, "n": v} for k, v in ref_agg.items()],
                       key=lambda x: -x["n"])[:8]

    # cihaz dağılımı (UA)
    mob = desk = 0
    for r in uarows:
        u = (r["ua"] or "").lower()
        if any(k in u for k in ("mobi", "android", "iphone", "ipad", "ipod")):
            mob += 1
        else:
            desk += 1

    return {"days": days, "series": series,
            "kpi": {"today": _rng(1), "d7": _rng(7), "d30": _rng(30),
                    "total": {"visits": total["v"] or 0, "uniq": total["u"] or 0}},
            "referrers": referrers, "device": {"mobile": mob, "desktop": desk},
            "bots_excluded": botcnt}


def engagement_stats(days=30):
    """Uygulama etkileşimi: en çok seçilen duygular, feedback dağılımı, favori/eşleşme sayısı."""
    since = (datetime.date.today() - datetime.timedelta(days=days - 1)).isoformat()
    with _conn() as c:
        moods = c.execute("""SELECT main, COUNT(*) n FROM mood_log WHERE date(ts)>=?
                             GROUP BY main ORDER BY n DESC""", (since,)).fetchall()
        fb = c.execute("""SELECT value, COUNT(*) n FROM feedback WHERE date(ts)>=?
                          GROUP BY value""", (since,)).fetchall()
        favs = c.execute("SELECT COUNT(*) n FROM favorites").fetchone()
        matches = c.execute("SELECT COUNT(*) n FROM mood_log WHERE date(ts)>=?", (since,)).fetchone()
    return {"moods": [dict(r) for r in moods],
            "feedback": {str(r["value"]): r["n"] for r in fb},
            "favorites": favs["n"] or 0, "matches": matches["n"] or 0}
