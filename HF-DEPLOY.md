# Keşf'i Hugging Face Spaces'e ücretsiz alma

Bu klasör HF Spaces (Docker) için hazır: `Dockerfile`, `requirements-deploy.txt`,
`.dockerignore` ve `README.md` başlığı. Torch **yok** — hafif ONNX (fastembed)
yolu kullanılır (~220 MB model, ücretsiz katmana rahat sığar).

## 1) Space oluştur
1. https://huggingface.co → giriş yap (ücretsiz hesap).
2. Sağ üst **New → Space**.
3. Ayarlar:
   - **Owner / Space name:** ör. `kullanici-adin/kesf`
   - **SDK:** **Docker** → *Blank* şablon
   - **Hardware:** *CPU basic* (ücretsiz)
   - **Visibility:** Public (ücretsizde önerilir)
4. **Create Space** → boş bir git deposu oluşur.

## 2) Kodu it (push)
Space oluşunca sana bir git adresi verir:
`https://huggingface.co/spaces/<kullanici>/<space>`

```bash
cd "C:/Users/saidz/Desktop/sekine-local"
git init                       # zaten repo değilse
git add Dockerfile requirements-deploy.txt .dockerignore README.md backend frontend data
git commit -m "Keşf ilk deploy"
git branch -M main
git remote add space https://huggingface.co/spaces/<kullanici>/<space>
git push space main
```
> İlk push'ta HF kullanıcı adı + **Access Token** ister (Settings → Access Tokens → *write* yetkili token oluştur, şifre yerine onu yapıştır).

## 3) Bekle ve aç
- HF otomatik olarak imajı kurar (torch olmadığı için hızlı; modeli imaja gömdüğümüz için ilk istek de hızlı).
- Birkaç dakikada **Running** olur → Space sayfasında uygulama açılır.
- Adres: `https://<kullanici>-<space>.hf.space`

## Notlar / sınırlar (ücretsiz katman)
- **Uyku:** bir süre kullanılmayınca Space uyur; ilk ziyarette ~30 sn'de uyanır.
- **SQLite kalıcı değil:** Space yeniden kurulunca `data/sekine.db` sıfırlanır
  (ruh hali/favori geçmişi silinir). Demo için sorun değil. Kalıcı isteniyorsa
  ücretsiz bir Postgres (Supabase/Neon) bağlanır — istersen ayrıca yaparız.
- **Kendi alan adın (keshf.online):** HF ücretsizde özel domain yok; alan adını
  `<...>.hf.space`'e yönlendiremezsin. Kendi domainin şartsa Render/Fly gibi bir
  yer + aynı Dockerfile kullanılır (orada da fastembed yolu sığar).

## Yerelde ne değişti
- Fazladan olan kök `.venv` silindi (~1.2 GB geri kazanıldı).
- Yerel geliştirme hâlâ `baslat.bat` ile `backend/.venv` üzerinden çalışır (değişmedi).
