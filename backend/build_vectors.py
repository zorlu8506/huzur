"""
Seed vektörlerini ÖNDEN hesaplayıp data/seed_vectors.json'a gömer.

Neden: canlıda (Render Free, 512 MB) embedding modeli sunucuda tutulmuyor;
seed'ler bir kez burada Gemini API ile çevrilir, dosya deploy'a commit'lenir.
Çalışma anında yalnızca kullanıcı sorgusu API'ye gider.

Kullanım (yerelde, bir kez — seed'ler değişince tekrar):
    PowerShell:  $env:JINA_API_KEY="jina_..."
    python build_data.py             # taxonomy.json güncel olsun
    python build_vectors.py

Sağlayıcı SEKINE_EMBEDDER ile seçilir (varsayılan: jina). Gemini için:
    $env:SEKINE_EMBEDDER="gemini"; $env:GEMINI_API_KEY="..."

Aynı embedding uzayı garanti edilsin diye router ile AYNI build_docs()'u kullanır
ve embedder imzasını dosyaya yazar (bkz. router_semantic._build).
"""
import os, json, sys, pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
os.environ.setdefault("SEKINE_EMBEDDER", "jina")

from embeddings import get_embedder
from router_semantic import build_docs, DATA, VECTORS


def main():
    tax = json.loads((DATA / "taxonomy.json").read_text(encoding="utf-8"))
    docs, meta = build_docs(tax)
    emb = get_embedder()
    if getattr(emb, "is_fallback", False) or not getattr(emb, "signature", None):
        raise SystemExit("HATA: API embedder yüklenemedi. GEMINI_API_KEY tanımlı mı? "
                         "SEKINE_EMBEDDER=gemini mi?")
    print(f"[build_vectors] {len(docs)} belge -> {emb.signature} ile çevriliyor...")
    vecs = emb.encode(docs)
    blob = {
        "signature": emb.signature,
        "count": len(vecs),
        "index": [{"main": m[0], "sub": m[1], "vec": v} for m, v in zip(meta, vecs)],
    }
    VECTORS.write_text(json.dumps(blob, ensure_ascii=False), encoding="utf-8")
    kb = VECTORS.stat().st_size / 1024
    print(f"[build_vectors] yazıldı: {VECTORS.name}  ({len(vecs)} vektör, {kb:.0f} KB)")


if __name__ == "__main__":
    main()
