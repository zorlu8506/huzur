# -*- coding: utf-8 -*-
"""16/32/48 PNG'leri tek bir favicon.ico içine gömer (PNG-tabanlı ICO, saf stdlib)."""
import struct, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sizes = [16, 32, 48]
imgs = [(s, (HERE / f"favicon-{s}.png").read_bytes()) for s in sizes]

hdr = struct.pack("<HHH", 0, 1, len(imgs))
entries = b""
offset = 6 + 16 * len(imgs)
for s, data in imgs:
    w = h = (0 if s >= 256 else s)
    entries += struct.pack("<BBBBHHII", w, h, 0, 0, 1, 32, len(data), offset)
    offset += len(data)
blob = hdr + entries + b"".join(d for _, d in imgs)
(HERE / "favicon.ico").write_bytes(blob)
print("favicon.ico yazıldı:", len(blob), "B (", ", ".join(f"{s}px" for s in sizes), ")")
