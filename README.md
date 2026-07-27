---
title: Keşf
emoji: 💧
colorFrom: indigo
colorTo: yellow
sdk: docker
app_port: 7860
pinned: false
short_description: Kur'an + Risale-i Nur + kanıta dayalı psikoloji ile huzura eşlik
---

<!-- Yukarıdaki blok Hugging Face Spaces içindir; sayfada görünmez. -->

# Keşf — Lokal (Backend + Frontend)

Psikolojik duruma göre **Kur'an-ı Kerim + Risale-i Nur + kanıta dayalı psikoloji**
üçlüsünü, dört katmanlı (Beden → Zihin → Kalp → Ruh) bir akışla sunan yapı.
Bu paket, statik prototipin canlıya taşınmış çekirdeğidir: kelime eşleştirme yerine
**embedding tabanlı anlamsal yönlendirme**.

## Ne var
```
sekine-local/
├─ backend/
│  ├─ app.py             FastAPI uçları + kriz güvenlik ağı + statik arayüz
│  ├─ router_semantic.py Anlamsal yönlendirme (metin → alt-duygu, cosine similarity)
│  ├─ embeddings.py      Lokal sentence-transformer (+ modelsiz dev fallback)
│  ├─ content.py         Alt-duygu → 4 katmanlı kart demeti (matristen)
│  ├─ db.py              SQLite: ruh hali takibi, feedback, favoriler
│  ├─ build_data.py      İçerik havuzu + taksonomiyi JSON'a üretir
│  └─ requirements.txt
├─ data/                 content.json + taxonomy.json (+ çalışınca sekine.db)
└─ frontend/index.html   API'ye bağlı arayüz
```

## Kurulum

### Kolay yol (çift tıkla)
- **Windows:** `baslat.bat` — ilk çalıştırmada sanal ortamı kurar, paketleri indirir, sunucuyu açar ve tarayıcıyı başlatır.
  - Torch inişini beklemeden hemen denemek için: `baslat-hizli.bat` (eşleştirme kalitesi düşük, arayüz/akış/grafik tam çalışır).
- **macOS / Linux:** `./baslat.sh` (ilk kez: `chmod +x baslat.sh`).

### Elle kurulum
```bash
cd sekine-local/backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python build_data.py          # data/*.json üretir (zaten var; değişiklik yaparsan tekrar çalıştır)
uvicorn app:app --reload --port 8000
```
Tarayıcı: **http://localhost:8000/**

İlk `/api/match` isteğinde embedding modeli iner (tek seferlik, sonra tamamen lokal
ve internetsiz çalışır). Model inene kadar açılış birkaç saniye sürebilir.

## Embedding modeli (anlamsal eşleştirmenin kalbi)
Varsayılan: `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` (Türkçe dahil, prefix'siz).
Türkçe'ye özel denemek için:
```bash
SEKINE_MODEL=emrecan/bert-base-turkish-cased-mean-nli-stsb-tr uvicorn app:app --port 8000
```
> Not: `dbmdz/bert-base-turkish-cased` bir masked-LM'dir; anlamsal benzerlik için
> **cümle-benzerliğine eğitilmiş** (NLI/STS) bir model kullan (yukarıdakiler gibi).

**Model olmadan denemek** (paketler yokken, düşük kaliteli fallback):
```bash
SEKINE_EMBEDDER=hash uvicorn app:app --port 8000
```

## API uçları
| Uç | Açıklama |
|---|---|
| `GET /api/taxonomy` | Ana + alt duygular (arayüz chip'leri) |
| `POST /api/match` | `{text}` **veya** `{main,sub}` → 4 katmanlı demet. Kriz ifadesi → güvenlik ağı |
| `POST /api/feedback` | `{main,sub,cards,value:-1|0|1}` → hangi içerik neye iyi geliyor |
| `POST /api/mood` | Günlük ruh hali kaydı |
| `GET /api/mood/summary?days=14` | Seyir + "bu hafta şu temaya ağırlık verelim" önerisi |
| `POST /api/favorites` / `GET /api/favorites` | Şifa Koleksiyonu |

## Mimari mantık
- **Yönlendirme (semantic):** her alt-duygunun `seeds` örnek cümleleri embed edilir;
  kullanıcı metni de embed edilir; en yakın alt-duygu seçilir. Türkçe çekimleri
  ("yalnızım", "korkuyorum") bu yüzden yakalar — kelime değil anlam eşleşir.
- **İçerik (matris):** hangi alt-duyguya hangi ayet/Risale/teknik geleceği
  `data/taxonomy.json` içindeki **uzman-onaylı matriste** tutulur (LLM'e ürettirilmez).
- **Kaynak ayrımı:** ayet/Risale metni havuzdan **çekilir**, üretilmez.

## Tamamlayıcı katmanlar (eklendi)
- **Temsil / Metafor (Kalp):** kıssalardan ilhamla kısa temsiller (Yunus a.s., tohum-filiz, ayna-güneş, kapıdaki misafir…) ilgili alt-duygulara bağlı.
- **Somatik hareket / duruş (Beden):** "duruş değişimi (somatik reset)" ve "su ile sıfırlama" — öfke/panik başta. Hadis ↔ somatik reset paralelliği.
- **Doğa / biyofili + sirkadiyen (Beden):** doğayla temas mikro-eylemleri; saate göre gündüz "ışığa çık" / gece "sessizliğe çekil" notu (backend saatten hesaplar).
- **Makam / ses (atmosfer):** ana duyguya göre makam önerisi + tarayıcıda **üretilen** kahverengi gürültü (dosya/telif gerektirmez; varsayılan kapalı). Lisanslı ney/makam kaydı sonra eklenebilir. *Makam-duygu eşleşmesi geleneksel/teoriktir; tedavi iddiası değildir.*
- **Ebru / akış tuvali (sanat):** panik/öfke anında 1 dakikalık, üretilen (telifsiz) serbest odak alanı.

## Sıradaki artımlar (bağlanmaya hazır)
- Ruh hali **seyir grafiği**: eklendi — üstteki "📈 Ruh Halim" (günlük duygu dağılımı + huzur çizgisi, 7/14/30 gün). Dolu görmek için `python seed_demo.py` ile örnek veri üretebilirsin (`--clear` ile silinir).
- Kişiselleştirme: `db.best_content()` geçmiş +1'lere göre içerik seçimini önceliklendirir
- **Söz Kartı** üretici (kartı canvas/görsel olarak indir-paylaş)
- İsteğe bağlı **ChromaDB** deposu (ölçeklenince; `router_semantic.py` içi belgelendi)
- Risale **orijinal + sade/şerh**: veri modelinde `orijinal` alanı hazır (arayüzde toggle çalışıyor)

## Güvenlik / sorumluluk
- Kriz ifadelerinde içerik önerilmez; doğrudan 112 + profesyonel/güvenilir desteğe yönlendirilir.
- Bu bir tedavi aracı değildir; terapinin yanında bir destektir. Efficacy (tedavi) iddiası taşımaz.
- Dinî metinler suçlayıcı değil, rahmet ve sığınak dilinde sunulur.
