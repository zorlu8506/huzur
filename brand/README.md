# Keşf — Marka Varlıkları

Slogan: **Kendini Keşfet** · Domain: **www.keshf.online**
İşaret: durgun yüzeye inen bir *nur damlası* + katman katman açılan *huzur halkaları*.

## Dosyalar

| Dosya | Ne için |
|---|---|
| `favicon.svg` | Modern tarayıcı favicon'u (vektör, her boyutta net) |
| `favicon.ico` | Klasik favicon (16/32/48 gömülü) |
| `apple-touch-icon.png` | 180×180, iOS ana ekran (koyu opak zemin) |
| `icon-192.png`, `icon-512.png` | PWA / manifest ikonları |
| `og-image.png` | 1200×630 sosyal paylaşım afişi |
| `logo-mark.svg` | Yalnız işaret (damla + halkalar) |
| `logo-horizontal.svg` / `.png` | Yatay kilit: işaret + “Keşf” (açık zemin metni #eef0ff) |
| `logo-vertical.svg` / `.png` | Dikey kilit: işaret üstte, “KEŞF” altta |
| `*-dark.svg` | Aynı kilitler, koyu metin (#1b1c46) — açık zeminler için |
| `head-snippet.html` | `<head>` içine yapıştırılacak `<link>`/OG etiketleri |
| `site.webmanifest` | PWA manifesti |

> Lockup SVG'lerine **Lora** fontu gömülüdür; her yerde birebir aynı dizilir.

## Kuruluma ekleme
1. Şu dosyaları sitenin kök dizinine koy: `favicon.svg`, `favicon.ico`,
   `apple-touch-icon.png`, `icon-192.png`, `icon-512.png`, `og-image.png`, `site.webmanifest`.
2. `head-snippet.html` içeriğini sayfanın `<head>` bölümüne yapıştır.

## Renkler (uygulamayla ortak)
`#0e1030` gece · `#f2c879` nur-altın · `#7c8be0` nur-soğuk ·
katmanlar: `#8fe0c4` beden · `#9db8f0` zihin · `#f4b98a` kalp · `#f2c879` ruh

## Yeniden üretmek
```
python build_assets.py     # SVG'ler + raster harness (Chrome ile PNG)
python build_ico.py        # 16/32/48 PNG'den favicon.ico
```
`_fonts/Lora-1.ttf` (weight 500) gömme için gereklidir.
