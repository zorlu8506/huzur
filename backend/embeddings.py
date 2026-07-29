"""
Embedding katmanı.

Üretim (önerilen): sentence-transformers ile TAMAMEN LOKAL, çok-dilli bir model.
  Varsayılan: sentence-transformers/paraphrase-multilingual-mpnet-base-v2
    - Türkçe dahil 50+ dil, cümle benzerliğine eğitilmiş, prefix gerektirmez.
  Türkçe'ye özel denemek istersen (genelde daha isabetli):
    SEKINE_MODEL=emrecan/bert-base-turkish-cased-mean-nli-stsb-tr

  ÖNEMLİ: 'dbmdz/bert-base-turkish-cased' bir masked-LM'dir; ham çıktısı
  cümle benzerliği için zayıftır. Anlamsal eşleştirmede yukarıdaki gibi
  cümle-benzerliğine eğitilmiş (NLI/STS) bir model kullan.

Geliştirme fallback: paketler yoksa deterministik bir hash-embedder devreye
girer; internetsiz çalışır ama kalitesi düşüktür. Sadece iskeleti denemek için.
Gerçek modeli açmak için:  pip install sentence-transformers
"""
import os, math, hashlib

MODEL_NAME = os.environ.get("SEKINE_MODEL", "sentence-transformers/paraphrase-multilingual-mpnet-base-v2")
_DIM_FALLBACK = 256


class _HashEmbedder:
    """Model yokken çalışsın diye basit, deterministik yer tutucu embedder."""
    is_fallback = True
    def __init__(self, dim=_DIM_FALLBACK):
        self.dim = dim
    def encode(self, texts):
        if isinstance(texts, str):
            texts = [texts]
        out = []
        for t in texts:
            vec = [0.0] * self.dim
            toks = t.lower().split()
            grams = toks + [a + b for a, b in zip(toks, toks[1:])]
            for g in grams:
                h = int(hashlib.md5(g.encode("utf-8")).hexdigest(), 16)
                vec[h % self.dim] += 1.0
            n = math.sqrt(sum(x * x for x in vec)) or 1.0
            out.append([x / n for x in vec])
        return out


class _STEmbedder:
    is_fallback = False
    def __init__(self, model_name):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)
    def encode(self, texts):
        if isinstance(texts, str):
            texts = [texts]
        return self.model.encode(texts, normalize_embeddings=True).tolist()


# ONNX tabanlı hafif embedder — torch GEREKTİRMEZ (üretim/ücretsiz host için).
# ~150 MB kurulum + ~220 MB model; 512 MB RAM'e sığar.
FE_MODEL = os.environ.get("SEKINE_FE_MODEL",
                          "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

class _FastEmbed:
    is_fallback = False
    def __init__(self, model_name):
        from fastembed import TextEmbedding
        import numpy as np
        self._np = np
        th = os.environ.get("FE_THREADS")           # düşük RAM'li host için 1 (opsiyonel)
        kwargs = {"threads": int(th)} if th else {}
        self.model = TextEmbedding(model_name=model_name, **kwargs)
    def encode(self, texts):
        if isinstance(texts, str):
            texts = [texts]
        out = []
        for v in self.model.embed(list(texts)):
            v = self._np.asarray(v, dtype="float32")
            n = float((v @ v) ** 0.5) or 1.0
            out.append((v / n).tolist())      # cosine için L2-normalize
        return out


_embedder = None

def get_embedder():
    global _embedder
    if _embedder is not None:
        return _embedder
    mode = os.environ.get("SEKINE_EMBEDDER", "").lower()
    if mode == "hash":
        _embedder = _HashEmbedder(); return _embedder
    if mode in ("jina", "api"):
        from embed_api import JinaEmbedder
        _embedder = JinaEmbedder()
        print(f"[embeddings] Jina API embedder: {_embedder.signature}")
        return _embedder
    if mode == "gemini":
        from embed_api import GeminiEmbedder
        _embedder = GeminiEmbedder()
        print(f"[embeddings] Gemini API embedder: {_embedder.signature}")
        return _embedder
    if mode == "fastembed":
        _embedder = _FastEmbed(FE_MODEL)
        print(f"[embeddings] fastembed (onnx) yüklendi: {FE_MODEL}")
        return _embedder
    if mode == "st":
        _embedder = _STEmbedder(MODEL_NAME)
        print(f"[embeddings] sentence-transformers yüklendi: {MODEL_NAME}")
        return _embedder
    # otomatik: önce hafif fastembed (onnx, torch'suz), sonra torch, sonra hash
    try:
        _embedder = _FastEmbed(FE_MODEL)
        print(f"[embeddings] fastembed (onnx) yüklendi: {FE_MODEL}")
    except Exception:
        try:
            _embedder = _STEmbedder(MODEL_NAME)
            print(f"[embeddings] model yüklendi: {MODEL_NAME}")
        except Exception as e:
            print(f"[embeddings] UYARI: embedder yüklenemedi ({e}). "
                  f"Geliştirme fallback (hash) — kalite düşük.")
            _embedder = _HashEmbedder()
    return _embedder


def cosine(a, b):
    return sum(x * y for x, y in zip(a, b))  # vektörler normalize edilmiş
