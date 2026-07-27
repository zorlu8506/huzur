"""
İsteğe bağlı: seyir grafiğini dolu görmek için ~2 haftalık örnek veri üretir.
Çalıştır:  python seed_demo.py      (gerçek kullanımda gerek yok, sadece demo)
Temizlemek için:  python seed_demo.py --clear
"""
import sys, sqlite3, datetime, random
import db as DB

MAINS = ["kaygi", "huzun", "ofke", "yalnizlik", "yeis", "tukenmislik", "korku"]
SUBS = {"kaygi": "istikbal", "huzun": "yas", "ofke": "haksizlik", "yalnizlik": "terk",
        "yeis": "genel", "tukenmislik": "yuk", "korku": "panik"}


def clear():
    with sqlite3.connect(DB.DB) as c:
        c.execute("DELETE FROM mood_log"); c.execute("DELETE FROM feedback")
    print("Demo verisi temizlendi.")


def seed():
    DB.init()
    today = datetime.date.today()
    rng = random.Random(7)
    with sqlite3.connect(DB.DB) as c:
        for i in range(14):
            d = today - datetime.timedelta(days=13 - i)
            # son günlere doğru 'kaygi' yoğunlaşsın (hint'i tetiklemek için)
            weights = [3, 1, 1, 1, 1, 1, 1] if i >= 10 else [1, 1, 1, 1, 1, 1, 1]
            for _ in range(rng.randint(1, 4)):
                m = rng.choices(MAINS, weights=weights)[0]
                ts = f"{d.isoformat()}T{rng.randint(8,22):02d}:00:00"
                c.execute("INSERT INTO mood_log(ts,main,sub) VALUES(?,?,?)", (ts, m, SUBS[m]))
                # huzur zamanla hafif yükselsin
                val = rng.choices([-1, 0, 1], weights=[max(1, 4 - i // 3), 3, i // 2 + 1])[0]
                c.execute("INSERT INTO feedback(ts,main,sub,layer,content_id,value) VALUES(?,?,?,?,?,?)",
                          (ts, m, SUBS[m], "ruh", "insirah6", val))
    print("14 günlük demo verisi eklendi. Arayüzde '📈 Ruh Halim'e bak.")


if __name__ == "__main__":
    clear() if "--clear" in sys.argv else seed()
