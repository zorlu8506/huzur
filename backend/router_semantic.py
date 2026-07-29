"""
Anlamsal yönlendirme (semantic routing).

Kelime eşleştirme yerine: her alt-duygunun 'seeds' örnek cümleleri embed edilir.
Kullanıcı metni de embed edilir; cosine similarity ile en yakın alt-duygu bulunur.
Türkçe çekimleri ("yalnızım", "korkuyorum") bu yüzden yakalar — kelime değil ANLAM eşleşir.

Varsayılan depo: bellek içi (küçük veri için yeterli).
İstersen ChromaDB'ye geç:  SEKINE_STORE=chroma  (bkz. chroma_store.py)
"""
import os, json, pathlib
from embeddings import get_embedder, cosine

DATA = pathlib.Path(__file__).resolve().parent.parent / "data"
VECTORS = DATA / "seed_vectors.json"


def build_docs(tax):
    """Yönlendirme belgeleri: her seed cümlesi + etiket + not -> (main, sub) etiketli.
    build_vectors.py ile router AYNI belge kümesini üretsin diye burada tek yerde tutulur."""
    docs, meta = [], []
    for mk, mv in tax.items():
        for sk, sv in mv["subs"].items():
            for phrase in sv.get("seeds", []) + [sv["label"], sv["note"]]:
                docs.append(phrase)
                meta.append((mk, sk))
    return docs, meta


class SemanticRouter:
    def __init__(self):
        self.tax = json.loads((DATA / "taxonomy.json").read_text(encoding="utf-8"))
        self.emb = get_embedder()
        self._index = []   # [(main, sub, vector)]
        self._build()

    def _build(self):
        # 1) Önceden hesaplanmış vektörler diskte varsa VE aynı embedding uzayından
        #    geliyorsa (imza eşleşmesi) onları kullan — seed'leri açılışta yeniden
        #    embed etmeyiz (API modunda cold-start'ı ~0'a indirir, çağrı harcamaz).
        sig = getattr(self.emb, "signature", None)
        if sig and VECTORS.exists():
            blob = json.loads(VECTORS.read_text(encoding="utf-8"))
            if blob.get("signature") == sig:
                self._index = [(r["main"], r["sub"], r["vec"]) for r in blob["index"]]
                print(f"[router] {len(self._index)} vektör diskten yüklendi (imza={sig}).")
                return
            print(f"[router] seed_vectors.json imzası uyuşmadı "
                  f"({blob.get('signature')} != {sig}); canlı üretiliyor.")
        # 2) Aksi halde (yerel geliştirme / fastembed) seed'leri anında embed et.
        docs, meta = build_docs(self.tax)
        vecs = self.emb.encode(docs)
        self._index = [(m[0], m[1], v) for m, v in zip(meta, vecs)]
        print(f"[router] {len(self._index)} yönlendirme vektörü hazır "
              f"({'FALLBACK' if getattr(self.emb,'is_fallback',False) else 'model'}).")

    def route(self, text, top_k=3):
        qv = self.emb.encode([text])[0]
        scored = {}
        for mk, sk, v in self._index:
            s = cosine(qv, v)
            key = (mk, sk)
            if s > scored.get(key, -1):
                scored[key] = s          # alt-duygunun en yakın seed'i o alt-duygunun skoru
        ranked = sorted(scored.items(), key=lambda kv: kv[1], reverse=True)
        best = ranked[0]
        return {
            "main": best[0][0],
            "sub": best[0][1],
            "score": round(float(best[1]), 4),
            "alternatives": [
                {"main": m, "sub": s, "score": round(float(sc), 4)}
                for (m, s), sc in ranked[1:top_k]
            ],
        }
