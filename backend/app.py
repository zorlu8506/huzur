"""
Sekine — FastAPI backend.
Çalıştır:  uvicorn app:app --reload --port 8000   (backend/ klasöründen)
Arayüz:    http://localhost:8000/
Sağlık:    http://localhost:8000/api/health
"""
import pathlib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

import db, content
from router_semantic import SemanticRouter

app = FastAPI(title="Sekine API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

ROUTER = None  # tembel yükleme (model ilk istekte yüklensin, açılış hızlansın)

CRISIS = ["intihar", "kendime zarar", "kendimi öldür", "yaşamak istemiyorum",
          "ölmek istiyorum", "canıma kıy", "yok olmak istiyorum", "hayatıma son"]

# Türkçe karakter katlama: şapkasız yazan kullanıcıda da kriz ağı devreye girsin.
# (örn. "yasamak istemiyorum" == "yaşamak istemiyorum")
_TR_FOLD = str.maketrans({"ş": "s", "ç": "c", "ğ": "g", "ı": "i", "ö": "o",
                          "ü": "u", "â": "a", "î": "i", "û": "u"})


def _fold(s: str) -> str:
    # önce Türkçe'ye özen: "İ"->"i", "I"->"ı" -> "i"
    return s.replace("İ", "i").replace("I", "ı").lower().translate(_TR_FOLD)


CRISIS_FOLDED = [_fold(w) for w in CRISIS]


@app.on_event("startup")
def _startup():
    db.init()


def _router():
    global ROUTER
    if ROUTER is None:
        ROUTER = SemanticRouter()
    return ROUTER


class MatchIn(BaseModel):
    text: Optional[str] = None
    main: Optional[str] = None
    sub: Optional[str] = None


class FeedbackIn(BaseModel):
    main: str; sub: str
    cards: List[Dict[str, Any]]     # her biri {layer, content_id}
    value: int                      # -1 | 0 | 1


class MoodIn(BaseModel):
    main: str; sub: str


class FavIn(BaseModel):
    main: str; sub: str; layer: str
    content_id: Optional[str] = None
    payload: Dict[str, Any]


@app.get("/api/health")
def health():
    r = _router()
    return {"ok": True, "fallback_embedder": getattr(r.emb, "is_fallback", False)}


@app.get("/api/taxonomy")
def taxonomy():
    return content.taxonomy_public()


@app.post("/api/match")
def match(inp: MatchIn):
    # 1) kriz güvenlik ağı — içerik önermeden önce (Türkçe karakter duyarsız)
    if inp.text and any(w in _fold(inp.text) for w in CRISIS_FOLDED):
        return {"crisis": True,
                "message": "Yazdıkların ağır bir yükü işaret ediyor olabilir. Lütfen 112'yi ara "
                           "ya da bir uzmana / güvendiğin birine ulaş. Yalnız değilsin."}
    # 2) alt-duyguyu belirle
    if inp.main and inp.sub:
        main, sub, routing = inp.main, inp.sub, None
    elif inp.text:
        r = _router().route(inp.text)
        main, sub, routing = r["main"], r["sub"], r
    else:
        return {"error": "text ya da (main+sub) gerekli."}
    # 3) 4 katmanlı demeti kur + takibi kaydet
    bundle = content.build_bundle(main, sub)
    bundle["routing"] = routing
    db.log_mood(main, sub)
    return bundle


@app.post("/api/feedback")
def feedback(inp: FeedbackIn):
    db.log_feedback(inp.main, inp.sub, inp.cards, inp.value)
    return {"ok": True}


@app.post("/api/mood")
def mood(inp: MoodIn):
    db.log_mood(inp.main, inp.sub)
    return {"ok": True}


@app.get("/api/mood/summary")
def mood_summary(days: int = 14):
    return db.mood_summary(days)


@app.get("/api/mood/trend")
def mood_trend(days: int = 14):
    return db.mood_trend(days)


@app.post("/api/favorites")
def add_fav(inp: FavIn):
    db.add_favorite(inp.main, inp.sub, inp.layer, inp.content_id, inp.payload)
    return {"ok": True}


@app.get("/api/favorites")
def favorites():
    return db.list_favorites()


# ---- statik arayüz ----
FRONT = pathlib.Path(__file__).resolve().parent.parent / "frontend"
if FRONT.exists():
    @app.get("/")
    def index():
        return FileResponse(str(FRONT / "index.html"))
    app.mount("/", StaticFiles(directory=str(FRONT)), name="frontend")
