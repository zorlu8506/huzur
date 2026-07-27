"""
Kalıcı veri (SQLite, stdlib — ek kurulum yok).
- mood_log: günlük ruh hali takibi -> haftalık/aylık seyir grafiği
- feedback: (-1/0/+1) -> hangi içerik hangi duyguya iyi geliyor (optimizasyon)
- favorites: 'Şifa Koleksiyonum / Sığınak'
Basit tutuldu: tek kullanıcı (local). Çok kullanıcıda user_id kolonu eklenir.
"""
import sqlite3, pathlib, datetime, json

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
