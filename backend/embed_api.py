"""
Uzak (API tabanlı) embedding — model sunucuda TUTULMAZ.

Neden: fastembed/onnx yolu RAM'de ~600 MB'a çıkıyordu ve Render Free (512 MB)
sığdıramıyordu. Bunun yerine:
  - build_vectors.py ile ~131 seed cümlesi BİR KEZ çevrilip data/seed_vectors.json'a
    gömülür (deploy'a commit'lenir);
  - çalışma anında yalnızca kullanıcının sorgusu embedding API'sine gider.
Böylece uygulama ~80 MB'ta kalır, Free'ye rahat sığar, soğuk başlangıç anındadır.

Sadece Python standart kütüphanesi (urllib) — ek runtime bağımlılığı YOK.

Sağlayıcılar:
  - Jina AI  (varsayılan, ücretsiz/faturasız katman)  ->  SEKINE_EMBEDDER=jina
      JINA_API_KEY          zorunlu (https://jina.ai/embeddings — ücretsiz anahtar)
      JINA_EMBED_MODEL      varsayılan: jina-embeddings-v3
      JINA_EMBED_DIM        varsayılan: 1024   (MRL; 32..1024)
  - Google Gemini  ->  SEKINE_EMBEDDER=gemini
      GEMINI_API_KEY (veya GOOGLE_API_KEY)   zorunlu
      GEMINI_EMBED_MODEL    varsayılan: gemini-embedding-001
      GEMINI_EMBED_DIM      varsayılan: 768

İki sağlayıcıda da seed vektörleri ile sorgu vektörü AYNI uzaydan gelmeli; embedder
bir "signature" taşır, data/seed_vectors.json bununla saklanır, uyuşmazsa router
diskteki vektörleri yok sayar (bkz. router_semantic._build).
"""
import os, json, math, time, urllib.request, urllib.error

_MAX_BATCH = 100            # tek çağrıda en fazla belge
_RETRY_CODES = (429, 500, 502, 503, 504)


def _l2(vec):
    n = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [x / n for x in vec]


def _post(url, headers, body, timeout):
    """Basit, yeniden denemeli JSON POST (stdlib)."""
    data = json.dumps(body).encode("utf-8")
    last = None
    # Not: Jina, Cloudflare arkasında; urllib'in varsayılan User-Agent'ini "1010"
    # ile bloklar. Normal bir UA vermek şart.
    base = {"Content-Type": "application/json",
            "User-Agent": "kesf/1.0 (+https://keshf.online)", "Accept": "application/json"}
    for attempt in range(3):
        req = urllib.request.Request(url, data=data,
                                     headers={**base, **headers},
                                     method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}: {e.read().decode('utf-8', 'ignore')[:300]}"
            if e.code in _RETRY_CODES and attempt < 2:
                time.sleep(1.5 * (attempt + 1)); continue
            raise RuntimeError(f"Embedding API hatası — {last}")
        except urllib.error.URLError as e:
            last = str(e)
            if attempt < 2:
                time.sleep(1.5 * (attempt + 1)); continue
            raise RuntimeError(f"Embedding ağ hatası — {last}")
    raise RuntimeError(f"Embedding başarısız — {last}")


class _BaseEmbedder:
    is_fallback = False

    def encode(self, texts):
        if isinstance(texts, str):
            texts = [texts]
        texts = list(texts)
        todo, seen = [], set()
        for t in texts:
            if t not in self._cache and t not in seen:
                seen.add(t); todo.append(t)
        for i in range(0, len(todo), _MAX_BATCH):
            chunk = todo[i:i + _MAX_BATCH]
            for t, v in zip(chunk, self._embed_batch(chunk)):
                self._cache[t] = v
        if len(self._cache) > 2000:                    # önbellek şişmesin
            self._cache = {t: self._cache[t] for t in texts}
        return [self._cache[t] for t in texts]


class JinaEmbedder(_BaseEmbedder):
    URL = "https://api.jina.ai/v1/embeddings"

    def __init__(self, model=None, dim=None, timeout=20):
        self.model = model or os.environ.get("JINA_EMBED_MODEL", "jina-embeddings-v3")
        self.dim = int(dim or os.environ.get("JINA_EMBED_DIM", "1024"))
        self.task = os.environ.get("JINA_EMBED_TASK", "text-matching")   # simetrik benzerlik
        self.timeout = timeout
        self.signature = f"jina:{self.model}:{self.dim}:{self.task}"
        self._cache = {}

    def _key(self):
        k = os.environ.get("JINA_API_KEY")
        if not k:
            raise RuntimeError("JINA_API_KEY tanımlı değil. https://jina.ai/embeddings "
                               "adresinden ücretsiz bir anahtar al ve ortam değişkeni ver.")
        return k

    def _embed_batch(self, texts):
        body = {"model": self.model, "task": self.task, "input": list(texts),
                "dimensions": self.dim, "embedding_type": "float"}
        out = _post(self.URL, {"Authorization": f"Bearer {self._key()}"}, body, self.timeout)
        data = out.get("data", [])
        if len(data) != len(texts):
            raise RuntimeError(f"Jina beklenmedik yanıt: {len(data)} vektör / {len(texts)} metin")
        data = sorted(data, key=lambda d: d.get("index", 0))   # sıra garanti
        return [_l2(d["embedding"]) for d in data]


class GeminiEmbedder(_BaseEmbedder):
    API = "https://generativelanguage.googleapis.com/v1beta"
    TASK = "SEMANTIC_SIMILARITY"

    def __init__(self, model=None, dim=None, timeout=20):
        self.model = model or os.environ.get("GEMINI_EMBED_MODEL", "gemini-embedding-001")
        self.dim = int(dim or os.environ.get("GEMINI_EMBED_DIM", "768"))
        self.timeout = timeout
        self.signature = f"gemini:{self.model}:{self.dim}:{self.TASK}"
        self._cache = {}

    def _key(self):
        k = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not k:
            raise RuntimeError("GEMINI_API_KEY tanımlı değil. https://aistudio.google.com/apikey")
        return k

    def _embed_batch(self, texts):
        reqs = [{
            "model": f"models/{self.model}",
            "content": {"parts": [{"text": t}]},
            "taskType": self.TASK,
            "outputDimensionality": self.dim,
        } for t in texts]
        url = f"{self.API}/models/{self.model}:batchEmbedContents?key={self._key()}"
        out = _post(url, {}, {"requests": reqs}, self.timeout)
        embs = out.get("embeddings", [])
        if len(embs) != len(texts):
            raise RuntimeError(f"Gemini beklenmedik yanıt: {len(embs)} vektör / {len(texts)} metin")
        return [_l2(e["values"]) for e in embs]
