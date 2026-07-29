# Keşf'i Render'a alma (ücretsiz katman) + keshf.online bağlama

Render bir **GitHub** deposundan çeker. Akış: kodu GitHub'a it → Render'da
Blueprint ile bağla → Gemini API anahtarını gir.

> ✅ **Bellek sorunu çözüldü.** Embedding modeli artık sunucuda **tutulmuyor**;
> seed'ler önceden `data/seed_vectors.json`'a gömülü, çalışma anında yalnızca
> kullanıcı sorgusu **Jina AI embedding API**'sine gidiyor. Uygulama ~80 MB →
> Render Free (512 MB) **rahat sığar**, soğuk başlangıç neredeyse anında.

## 0) Jina API anahtarı al (ücretsiz, faturasız)
1. https://jina.ai/embeddings → sayfada hazır bir **ücretsiz anahtar** verilir
   (kredi kartı gerekmez); daha fazla token için üye ol.
2. Anahtarı kopyala (`jina_...`).
   > Ücretsiz token bu kullanım için fazlasıyla yeterli (sorgular çok kısa).

## 0.5) Seed vektörlerini üret (yerelde, bir kez — seed'ler değişince tekrar)
```bash
cd "C:/Users/saidz/Desktop/sekine-local/backend"
# PowerShell:
$env:JINA_API_KEY="jina_...";  python build_data.py;  python build_vectors.py
```
Bu, `data/seed_vectors.json`'u üretir. **Commit'le** (deploy bunu kullanır).
> Not: seed vektörleri ile canlıdaki sorgu vektörü **aynı modelden** gelmeli;
> dosya bir "imza" taşır, uyuşmazsa sunucu diskteki vektörleri yok sayar.

## 1) Kodu GitHub'a it
```bash
cd "C:/Users/saidz/Desktop/sekine-local"
git add -A && git commit -m "API embedding'e geçiş"
git push
```
> Repo zaten bağlı: `github.com/zorlu8506/huzur`.

## 2) Render'da servis oluştur
1. https://render.com → giriş (GitHub ile).
2. **New + → Blueprint** → repoyu seç → Render `render.yaml`'i okur (Docker servisi).
3. `JINA_API_KEY` **sync:false** (gizli) olarak tanımlı → Render onu **sormaz**;
   servis oluşunca **Environment** sekmesine gir, `JINA_API_KEY` = anahtarını
   ekle, **Save** (deploy tetiklenir).
4. Adres: `https://kesf.onrender.com` (isme göre değişir).

## 3) keshf.online'ı bağla
1. Render servis → **Settings → Custom Domains → Add** → `keshf.online` ve
   `www.keshf.online` ekle.
2. Render sana hedef verir. Domain sağlayıcının DNS panelinde:
   - `www` → CNAME → Render'ın verdiği adres
   - kök `keshf.online` → Render'ın A kaydı (veya ALIAS/ANAME)
3. DNS yayılınca Render otomatik ücretsiz SSL verir.

## Sağlık kontrolü
`https://<adres>/api/health` →
`{"ok":true, "embedder":"jina:jina-embeddings-v3:1024:text-matching", "routes":131}`
- `embedder` "jina..." ise API yolu aktif; "Hash..." görürsen anahtar/env eksik.
- `routes` seed vektör sayısı (diskten yüklendiyse çağrı harcamadan gelir).

## Notlar (ücretsiz katman)
- **Uyku:** 15 dk hareketsizlikte uyur; ilk istek ~30 sn (soğuk başlangıç — artık
  model inmediği için hızlı).
- **API bağımlılığı:** Jina erişilemezse `/api/match` sorgusu hata döner (seed'ler
  yine diskten gelir). Ücretsiz token bu kullanımda pratikte dolmaz.
- **SQLite kalıcı değil:** her yeni deploy'da `data/sekine.db` sıfırlanır. Kalıcı
  istenirse ücretsiz Postgres bağlanır.
- Aynı `Dockerfile` HF Spaces'te de çalışır (orada da `JINA_API_KEY` secret'ı gir).
- Gemini yolu da kodda duruyor (`SEKINE_EMBEDDER=gemini` + `GEMINI_API_KEY`); ileride
  ücretli/gizlilik istenirse tek env değişikliğiyle geçilebilir (seed'ler o zaman
  `build_vectors.py` ile yeniden üretilmeli — imza değişir).
