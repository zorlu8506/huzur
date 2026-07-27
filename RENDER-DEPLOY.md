# Keşf'i Render'a alma (ücretsiz katman) + keshf.online bağlama

Render, HF'in aksine doğrudan `git push` almaz; bir **GitHub (veya GitLab)**
deposundan çeker. Akış: kodu GitHub'a it → Render'da Blueprint ile bağla.

> ⚠️ Ücretsiz katman **512 MB RAM**. Model ölçümü ~740 MB çıktı; Render Free'de
> **OOM (çökme) ihtimali yüksek**. Bellek kısıcılar eklendi (thread=1, arena=2)
> ama garanti değil. Çökerse: (a) planı **Starter/Standard**'a yükselt, ya da
> (b) embedding'i API'ye taşıyalım (uygulama minik kalır, Free'ye sığar).

## 1) Kodu GitHub'a it
```bash
cd "C:/Users/saidz/Desktop/sekine-local"
# GitHub'da bos bir repo ac: github.com/new  (orn: kesf)
git remote add origin https://github.com/<kullanici>/kesf.git
git push -u origin main
```
> Push'ta GitHub kullanıcı adı + **Personal Access Token** (Settings → Developer
> settings → Tokens) ister; şifre yerine onu yapıştır.

## 2) Render'da servis oluştur
1. https://render.com → giriş (GitHub ile giriş en kolayı).
2. **New + → Blueprint** → GitHub reposunu seç → Render `render.yaml`'i okur,
   Docker servisi olarak kurar. (Blueprint görünmezse: **New + → Web Service →
   Docker** → repo seç; port/health otomatik gelir.)
3. **Create** → ilk build birkaç dakika (imaj kurulur, model imaja gömülür).
4. Adres: `https://kesf.onrender.com` (isme göre değişir).

## 3) keshf.online'ı bağla
1. Render servis → **Settings → Custom Domains → Add** → `keshf.online` ve
   `www.keshf.online` ekle.
2. Render sana bir hedef verir (CNAME/A kaydı). Domain sağlayıcının DNS panelinde:
   - `www` → CNAME → Render'ın verdiği adres
   - kök `keshf.online` → Render'ın A kaydı (veya ALIAS/ANAME)
3. DNS yayılınca (dakikalar–saatler) Render otomatik ücretsiz SSL verir.

## Notlar (ücretsiz katman)
- **Uyku:** 15 dk hareketsizlikte uyur; ilk istek ~30–60 sn (soğuk başlangıç).
- **SQLite kalıcı değil:** her yeni deploy'da `data/sekine.db` sıfırlanır
  (ruh hali/favori geçmişi silinir). Kalıcı istenirse ücretsiz Postgres bağlanır.
- Aynı `Dockerfile` HF Spaces'te de çalışır; Render'da olmazsa oraya dönebiliriz.
