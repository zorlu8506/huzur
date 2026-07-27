"""Gerçek embedding modeliyle router kalite testi (in-process, sunucu gerektirmez)."""
import sys, time
sys.path.insert(0, ".")
from router_semantic import SemanticRouter

CASES = [
    ("gelecekten çok korkuyorum, ne olacak bilmiyorum", "kaygi/istikbal"),
    ("kendimi çok yalnız hissediyorum, kimse beni anlamıyor", "yalnizlik/anlasilmamak"),
    ("bu haksızlığa çok öfkeliyim, içim yanıyor", "ofke/haksizlik"),
    ("hiçbir şeyin anlamı kalmadı, boşluktayım", "huzun/anlamsizlik"),
    ("çok yorgunum, tükendim, hiçbir şeye enerjim yok", "tukenmislik/*"),
    ("param yetmeyecek diye geceleri uyuyamıyorum", "kaygi/rizik"),
    ("beni terk etti, bir başıma kaldım", "yalnizlik/terk"),
    ("kendimi affedemiyorum, yaptığım hata aklımdan çıkmıyor", "yeis/affedememe"),
    ("birden kalbim hızlandı, boğuluyormuş gibi oldum", "korku/panik"),
    ("aklıma kötü kötü düşünceler geliyor durduramıyorum", "korku/vesvese"),
]

t0 = time.time()
r = SemanticRouter()
print(f"[hazir] model yuklendi, {time.time()-t0:.1f}s\n")
ok = 0
for text, beklenen in CASES:
    res = r.route(text)
    got = f"{res['main']}/{res['sub']}"
    hit = (got == beklenen) or (beklenen.endswith("/*") and res['main'] == beklenen.split("/")[0])
    ok += hit
    alt = ", ".join(f"{a['main']}/{a['sub']}({a['score']})" for a in res.get("alternatives", []))
    print(f"{'OK ' if hit else 'XX '} beklenen={beklenen:24} -> {got} (skor {res['score']})")
    print(f"     metin: {text}")
    print(f"     alt:   {alt}\n")
print(f"=== isabet: {ok}/{len(CASES)} ===")
