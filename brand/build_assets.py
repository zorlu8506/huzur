# -*- coding: utf-8 -*-
"""Keşf marka varlıkları üretici: SVG'ler + raster için HTML harness + ICO birleştirme."""
import base64, pathlib, struct, sys

HERE = pathlib.Path(__file__).resolve().parent
FONTS = HERE / "_fonts"
REND = HERE / "_render"
REND.mkdir(exist_ok=True)

# --- Lora fontu (varsa göm) ---
def font_face():
    f = FONTS / "Lora-1.ttf"     # weight 500
    if not f.exists():
        return "", "'Iowan Old Style','Palatino Linotype',Palatino,Georgia,'Times New Roman',serif"
    b64 = base64.b64encode(f.read_bytes()).decode()
    css = ("@font-face{font-family:'LoraEmb';font-style:normal;font-weight:500;"
           "src:url(data:font/ttf;base64,%s) format('truetype');}" % b64)
    return css, "'LoraEmb','Palatino Linotype',Georgia,serif"

FONT_CSS, SERIF = font_face()

# --- ortak işaret (mark) ---
DEFS = """<defs>
  <radialGradient id="d" cx="42%" cy="34%" r="72%">
    <stop offset="0%" stop-color="#fff4d8"/>
    <stop offset="52%" stop-color="#f2c879"/>
    <stop offset="100%" stop-color="#d99a3d"/>
  </radialGradient>
</defs>"""

def mark(ripples=True, highlight=True):
    r = ""
    if ripples:
        r = """<g stroke="#f2c879" fill="none" stroke-width="1.4" stroke-linecap="round">
    <ellipse cx="50" cy="104" rx="30" ry="7.5" opacity=".16"/>
    <ellipse cx="50" cy="104" rx="20" ry="5" opacity=".30"/>
    <ellipse cx="50" cy="104" rx="10" ry="2.6" opacity=".50"/>
  </g>"""
    h = ('<ellipse cx="41" cy="46" rx="7" ry="11" fill="#fff" opacity=".38" '
         'transform="rotate(-18 41 46)"/>') if highlight else ""
    return ('%s\n  %s\n  <path d="M50 10 C64 30 80 45 80 60 A30 30 0 1 1 20 60 '
            'C20 45 36 30 50 10 Z" fill="url(#d)"/>\n  %s' % (DEFS, r, h))

MARK_VB = "0 0 100 128"

def svg(vb, inner, extra_defs=""):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="%s">%s%s</svg>\n'
            % (vb, extra_defs, inner))

# 1) favicon.svg + logo-mark.svg (şeffaf, ölçeklenebilir)
(HERE / "favicon.svg").write_text(svg(MARK_VB, mark()), encoding="utf-8")
(HERE / "logo-mark.svg").write_text(svg(MARK_VB, mark()), encoding="utf-8")

# 2) yatay lockup — işaret + "Keşf" (gömülü Lora)
def lockup_h(fill):
    inner = ('<style>%s</style>' % FONT_CSS +
             '<g transform="translate(4,12) scale(0.74)">%s</g>' % mark() +
             '<text x="92" y="80" font-family=%r font-size="66" font-weight="500" '
             'fill="%s" letter-spacing="1">Keşf</text>' % (SERIF, fill))
    return svg("0 0 250 122", inner)

(HERE / "logo-horizontal.svg").write_text(lockup_h("#eef0ff"), encoding="utf-8")
(HERE / "logo-horizontal-dark.svg").write_text(lockup_h("#1b1c46"), encoding="utf-8")

# 3) dikey lockup — işaret üstte, "KEŞF" altta
def lockup_v(fill):
    inner = ('<style>%s</style>' % FONT_CSS +
             '<g transform="translate(43,4) scale(0.74)">%s</g>' % mark() +
             '<text x="80" y="180" text-anchor="middle" font-family=%r font-size="34" '
             'font-weight="500" fill="%s" letter-spacing="6">KEŞF</text>' % (SERIF, fill))
    return svg("0 0 160 196", inner)

(HERE / "logo-vertical.svg").write_text(lockup_v("#eef0ff"), encoding="utf-8")
(HERE / "logo-vertical-dark.svg").write_text(lockup_v("#1b1c46"), encoding="utf-8")

# 4) raster harness HTML'leri  -> (isim, W, H)
def html_page(body_css, inner, w, h):
    return ("<!doctype html><meta charset=utf-8><style>*{margin:0;padding:0}"
            "html,body{width:%dpx;height:%dpx;overflow:hidden}%s</style>%s"
            % (w, h, body_css, inner))

RASTERS = []  # (html_dosya, png_dosya, W, H)

# transparan işaret PNG'leri (favicon + pwa ikon)
for name, px in [("favicon-16", 16), ("favicon-32", 32), ("favicon-48", 48),
                 ("icon-192", 192), ("icon-512", 512)]:
    body = "body{display:grid;place-items:center}svg{width:%dpx;height:%dpx}" % (px, px)
    page = html_page(body, svg("0 0 100 100", mark(ripples=(px>=48))), px, px)
    f = REND / (name + ".html"); f.write_text(page, encoding="utf-8")
    RASTERS.append((f.name, name + ".png", px, px))

# apple-touch-icon: koyu opak zemin (Apple şeffaflık sevmez)
apple = html_page(
    "body{width:180px;height:180px;background:radial-gradient(120% 120% at 50% 20%,#2b2a63,#0e1030);"
    "display:grid;place-items:center}svg{width:120px;height:120px}",
    svg("0 0 100 100", mark()), 180, 180)
(REND / "apple.html").write_text(apple, encoding="utf-8")
RASTERS.append(("apple.html", "apple-touch-icon.png", 180, 180))

# og-image: 1200x630 paylaşım afişi
og_body = ("""
body{width:1200px;height:630px;color:#eef0ff;font-family:%s;position:relative;
  background:radial-gradient(120%% 90%% at 50%% 118%%,#3a3170 0%%,rgba(58,49,112,0) 55%%),
             linear-gradient(180deg,#0e1030 0%%,#1b1c46 55%%,#2b2a63 100%%);}
.stars{position:absolute;inset:0;opacity:.5;background-image:
  radial-gradient(2px 2px at 12%% 26%%,#fff,transparent),
  radial-gradient(2px 2px at 72%% 18%%,#dfe3ff,transparent),
  radial-gradient(1.6px 1.6px at 40%% 72%%,#fff,transparent),
  radial-gradient(1.6px 1.6px at 88%% 64%%,#cfd6ff,transparent),
  radial-gradient(2px 2px at 58%% 40%%,#fff,transparent);}
.row{position:absolute;inset:0;display:flex;align-items:center;gap:56px;padding:0 110px;}
.mk{width:200px;height:256px;flex:none;filter:drop-shadow(0 18px 40px rgba(0,0,0,.5));}
h1{font-size:132px;font-weight:500;letter-spacing:2px;line-height:1;margin:0}
.tag{font-style:italic;font-size:44px;color:#f6d9a0;margin-top:18px}
.url{font-family:system-ui,sans-serif;font-size:24px;letter-spacing:6px;text-transform:uppercase;
  color:#8b8fc4;margin-top:26px}
<style-endsentinel>""" % SERIF).replace("<style-endsentinel>", "")
og_inner = ('<style>%s</style>' % FONT_CSS +
    '<div class="stars"></div><div class="row">'
    '<div class="mk">%s</div>'
    '<div><h1>Keşf</h1><div class="tag">Kendini Keşfet</div>'
    '<div class="url">www.keshf.online</div></div></div>'
    % svg(MARK_VB, mark()))
(REND / "og.html").write_text(html_page(og_body, og_inner, 1200, 630), encoding="utf-8")
RASTERS.append(("og.html", "og-image.png", 1200, 630))

# render listesini shell'e yaz
(REND / "list.txt").write_text(
    "\n".join("%s|%s|%d|%d" % r for r in RASTERS), encoding="utf-8")
print("SVG'ler ve %d raster harness yazıldı. serif=%s" % (len(RASTERS), SERIF[:24]))
