"""
İçerik çözümleme: bir alt-duygu -> 4 katmanlı kart demeti (nefis/akıl/kalp/ruh).
Matristeki ID'ler havuzdan çözülür, katman başına bir mikro-eylem eklenir.
Rotasyon: aynı alt-duyguda arka arkaya aynı bileşim gelmesin diye son seçim hatırlanır.
"""
import json, pathlib, random, datetime

DATA = pathlib.Path(__file__).resolve().parent.parent / "data"
_C = json.loads((DATA / "content.json").read_text(encoding="utf-8"))
_T = json.loads((DATA / "taxonomy.json").read_text(encoding="utf-8"))
_last = {}  # rotasyon hafızası


def _pick(ids, tag):
    if len(ids) == 1:
        return ids[0]
    prev = _last.get(tag)
    choice = prev
    while choice == prev:
        choice = random.choice(ids)
    _last[tag] = choice
    return choice


def _micro(layer):
    return random.choice(_C["micro"][layer])


def sub_info(main, sub):
    return _T[main]["subs"][sub]


def variants_count(main, sub):
    s = sub_info(main, sub)
    return len(s["nefis"]) * len(s["akil"]) * len(s["kalp"]) * len(s["ruh"])


def build_bundle(main, sub):
    s = sub_info(main, sub)
    n = _C["somatik"][_pick(s["nefis"], f"{sub}-n")]
    a = _C["bilissel"][_pick(s["akil"], f"{sub}-a")]
    k_id = _pick(s["kalp"], f"{sub}-k"); k = _C["risale"][k_id]
    r_id = _pick(s["ruh"], f"{sub}-r"); r = _C["ayet"][r_id]

    # temsil (kıssa/metafor) — Kalp katmanına eşlik eder
    temsil = None
    if s.get("kissa"):
        kis = _C["kissa"][_pick(s["kissa"], f"{sub}-t")]
        temsil = {"text": kis["text"], "ref": kis["ref"]}

    # sirkadiyen (saate duyarlı) yönlendirme
    hour = datetime.datetime.now().hour
    circadian = _C["circadian"]["gunduz"] if 7 <= hour < 19 else _C["circadian"]["gece"]

    cards = [
        {"layer": "nefis", "layer_name": "Beden", "layer_sub": "Nefis · sakinleşme",
         "title": n["title"], "intro": n["intro"],
         "breath": n.get("breath"), "steps": n.get("steps"),
         "circadian": circadian,
         "micro": _micro("nefis")},
        {"layer": "akil", "layer_name": "Zihin", "layer_sub": "Akıl · bilişsel esneklik",
         "school": a["school"], "title": a["title"], "intro": a["intro"], "steps": a["steps"],
         "micro": _micro("akil")},
        {"layer": "kalp", "layer_name": "Kalp", "layer_sub": "Risale-i Nur · teselli",
         "content_id": k_id, "sade": k["sade"], "orijinal": k.get("orijinal"),
         "ref": k["ref"], "kaynak": k.get("kaynak"),
         "temsil": temsil,
         "micro": _micro("kalp")},
        {"layer": "ruh", "layer_name": "Ruh", "layer_sub": "Kur'an-ı Kerim · mânâ",
         "content_id": r_id, "arabic": r["ar"], "meal": r["meal"], "ref": r["ref"],
         "micro": _micro("ruh")},
    ]
    return {
        "main": main, "sub": sub,
        "label": _T[main]["label"] + " · " + s["label"],
        "note": s["note"],
        "variants": variants_count(main, sub),
        "makam": _C["makam"].get(main),
        "cards": cards,
    }


def taxonomy_public():
    """Arayüzün chip'leri çizmesi için sade taksonomi (seeds hariç)."""
    return {mk: {"label": mv["label"],
                 "subs": {sk: {"label": sv["label"]} for sk, sv in mv["subs"].items()}}
            for mk, mv in _T.items()}
