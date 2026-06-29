from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, date


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI(title="Ikas-Txiki Manager API")
api_router = APIRouter(prefix="/api")


# ---------- Helpers ----------
def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id() -> str:
    return str(uuid.uuid4())


CATEGORIES = [
    {"name": "Prebenjamín", "min_age": 6, "max_age": 7},
    {"name": "Benjamín", "min_age": 8, "max_age": 9},
    {"name": "Alevín", "min_age": 10, "max_age": 11},
    {"name": "Infantil", "min_age": 12, "max_age": 13},
    {"name": "Cadete", "min_age": 14, "max_age": 15},
    {"name": "Juvenil", "min_age": 16, "max_age": 18},
]


def compute_category(birthdate: Optional[str]) -> Optional[str]:
    if not birthdate:
        return None
    try:
        bd = datetime.fromisoformat(birthdate).date() if "T" in birthdate or "-" in birthdate else None
        if bd is None:
            return None
    except Exception:
        try:
            bd = datetime.strptime(birthdate[:10], "%Y-%m-%d").date()
        except Exception:
            return None
    today = date.today()
    # Football season age: age reached during the season year
    season_year = today.year if today.month >= 7 else today.year - 1
    age = season_year - bd.year
    for c in CATEGORIES:
        if c["min_age"] <= age <= c["max_age"]:
            return c["name"]
    if age < 6:
        return "Querubín"
    return "Senior"


def clean(doc: dict) -> dict:
    doc.pop("_id", None)
    return doc


# ---------- Generic CRUD factory ----------
async def list_docs(coll: str, query: dict = None):
    cursor = db[coll].find(query or {}, {"_id": 0}).sort("created_at", -1)
    return await cursor.to_list(5000)


async def get_doc(coll: str, _id: str):
    doc = await db[coll].find_one({"id": _id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="No encontrado")
    return doc


async def insert_doc(coll: str, data: dict):
    data["id"] = new_id()
    data["created_at"] = now_iso()
    data["updated_at"] = now_iso()
    await db[coll].insert_one(dict(data))
    return clean(data)


async def update_doc(coll: str, _id: str, data: dict):
    existing = await db[coll].find_one({"id": _id})
    if not existing:
        raise HTTPException(status_code=404, detail="No encontrado")
    data = {k: v for k, v in data.items() if v is not None or k in data}
    data["updated_at"] = now_iso()
    await db[coll].update_one({"id": _id}, {"$set": data})
    return await get_doc(coll, _id)


async def delete_doc(coll: str, _id: str):
    res = await db[coll].delete_one({"id": _id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No encontrado")
    return {"ok": True}


# ================= PLAYERS =================
class Player(BaseModel):
    # Datos del formulario
    fecha_inscripcion: Optional[str] = None
    email_formulario: Optional[str] = None
    nombre: str
    apellidos: Optional[str] = ""
    fecha_nacimiento: Optional[str] = None
    centro_escolar: Optional[str] = None
    # Progenitores
    progenitor1_nombre: Optional[str] = None
    progenitor1_telefono: Optional[str] = None
    progenitor1_email: Optional[str] = None
    progenitor2_nombre: Optional[str] = None
    progenitor2_telefono: Optional[str] = None
    progenitor2_email: Optional[str] = None
    domicilio: Optional[str] = None
    # Deportivos / administrativos
    foto: Optional[str] = None  # base64 data url
    categoria: Optional[str] = None
    equipo_id: Optional[str] = None
    dorsal: Optional[str] = None
    posicion: Optional[str] = None
    estado: str = "pendiente_documentacion"  # activo, baja, lesionado, pendiente_documentacion, en_prueba
    numero_licencia: Optional[str] = None
    fecha_alta: Optional[str] = None
    fecha_baja: Optional[str] = None
    nueva_incorporacion: bool = False
    segundo_hermano: bool = False
    hermano_vinculado: Optional[str] = None
    descuento: Optional[float] = 0
    observaciones: Optional[str] = None
    familia_id: Optional[str] = None
    # Salud
    alergias: Optional[str] = None
    enfermedades: Optional[str] = None
    medicacion: Optional[str] = None
    seguro_medico: Optional[str] = None
    contacto_emergencia: Optional[str] = None
    telefono_emergencia: Optional[str] = None
    observaciones_medicas: Optional[str] = None
    # Equipación
    talla_camiseta: Optional[str] = None
    talla_pantalon: Optional[str] = None
    talla_chandal: Optional[str] = None
    talla_medias: Optional[str] = None
    talla_calzado: Optional[str] = None
    equipacion_entregada: bool = False
    fecha_entrega_equipacion: Optional[str] = None
    observaciones_material: Optional[str] = None
    # Documentación
    doc_dni_jugador: bool = False
    doc_dni_tutor: bool = False
    doc_foto: bool = False
    doc_autorizacion: bool = False
    doc_justificante_pago: bool = False
    doc_ficha_federativa: bool = False
    estado_documental: str = "pendiente"  # completo, pendiente, incompleto
    fecha_revision_doc: Optional[str] = None
    observaciones_doc: Optional[str] = None


@api_router.post("/players")
async def create_player(player: Player):
    data = player.model_dump()
    if not data.get("fecha_inscripcion"):
        data["fecha_inscripcion"] = now_iso()
    if data.get("fecha_nacimiento"):
        data["categoria"] = compute_category(data["fecha_nacimiento"])
    return await insert_doc("players", data)


@api_router.get("/players")
async def get_players(equipo_id: Optional[str] = None, estado: Optional[str] = None,
                      categoria: Optional[str] = None, q: Optional[str] = None):
    query: Dict[str, Any] = {}
    if equipo_id:
        query["equipo_id"] = equipo_id
    if estado:
        query["estado"] = estado
    if categoria:
        query["categoria"] = categoria
    docs = await list_docs("players", query)
    if q:
        ql = q.lower()
        docs = [d for d in docs if ql in (f"{d.get('nombre','')} {d.get('apellidos','')}").lower()]
    return docs


@api_router.get("/players/{player_id}")
async def get_player(player_id: str):
    return await get_doc("players", player_id)


@api_router.put("/players/{player_id}")
async def edit_player(player_id: str, player: Player):
    data = player.model_dump()
    if data.get("fecha_nacimiento"):
        data["categoria"] = compute_category(data["fecha_nacimiento"])
    return await update_doc("players", player_id, data)


@api_router.delete("/players/{player_id}")
async def remove_player(player_id: str):
    return await delete_doc("players", player_id)


# ================= FAMILIES =================
class Family(BaseModel):
    progenitor1_nombre: Optional[str] = None
    progenitor1_telefono: Optional[str] = None
    progenitor1_email: Optional[str] = None
    progenitor2_nombre: Optional[str] = None
    progenitor2_telefono: Optional[str] = None
    progenitor2_email: Optional[str] = None
    domicilio: Optional[str] = None
    contacto_principal: Optional[str] = None
    preferencia_comunicacion: Optional[str] = "email"  # email, telefono, whatsapp
    observaciones: Optional[str] = None


@api_router.post("/families")
async def create_family(family: Family):
    return await insert_doc("families", family.model_dump())


@api_router.get("/families")
async def get_families():
    fams = await list_docs("families")
    players = await list_docs("players")
    for f in fams:
        linked = [p for p in players if p.get("familia_id") == f["id"]]
        f["num_hijos"] = len(linked)
        f["hijos"] = [{"id": p["id"], "nombre": f"{p.get('nombre','')} {p.get('apellidos','')}"} for p in linked]
    return fams


@api_router.get("/families/{family_id}")
async def get_family(family_id: str):
    return await get_doc("families", family_id)


@api_router.put("/families/{family_id}")
async def edit_family(family_id: str, family: Family):
    return await update_doc("families", family_id, family.model_dump())


@api_router.delete("/families/{family_id}")
async def remove_family(family_id: str):
    return await delete_doc("families", family_id)


# ================= TEAMS =================
class Team(BaseModel):
    nombre: str
    categoria: Optional[str] = None
    temporada: Optional[str] = None
    entrenador: Optional[str] = None
    segundo_entrenador: Optional[str] = None
    delegado: Optional[str] = None
    dias_entrenamiento: Optional[str] = None
    horario: Optional[str] = None
    campo: Optional[str] = None
    limite_jugadores: Optional[int] = 20
    estado: str = "activo"  # activo, cerrado, pendiente


@api_router.post("/teams")
async def create_team(team: Team):
    return await insert_doc("teams", team.model_dump())


@api_router.get("/teams")
async def get_teams():
    teams = await list_docs("teams")
    players = await list_docs("players")
    for t in teams:
        t["num_jugadores"] = len([p for p in players if p.get("equipo_id") == t["id"]])
    return teams


@api_router.get("/teams/{team_id}")
async def get_team(team_id: str):
    team = await get_doc("teams", team_id)
    players = await list_docs("players", {"equipo_id": team_id})
    team["jugadores"] = players
    return team


@api_router.put("/teams/{team_id}")
async def edit_team(team_id: str, team: Team):
    return await update_doc("teams", team_id, team.model_dump())


@api_router.delete("/teams/{team_id}")
async def remove_team(team_id: str):
    return await delete_doc("teams", team_id)


# ================= MATCHES =================
class Match(BaseModel):
    temporada: Optional[str] = None
    jornada: Optional[str] = None
    fecha: Optional[str] = None
    hora: Optional[str] = None
    equipo_id: Optional[str] = None
    rival: Optional[str] = None
    condicion: str = "local"  # local, visitante
    campo: Optional[str] = None
    direccion_campo: Optional[str] = None
    tipo: str = "liga"  # liga, copa, amistoso, torneo
    estado: str = "programado"  # programado, jugado, aplazado, suspendido, cancelado
    resultado_propio: Optional[int] = None
    resultado_rival: Optional[int] = None
    observaciones: Optional[str] = None


@api_router.post("/matches")
async def create_match(match: Match):
    return await insert_doc("matches", match.model_dump())


@api_router.get("/matches")
async def get_matches(equipo_id: Optional[str] = None, estado: Optional[str] = None):
    query: Dict[str, Any] = {}
    if equipo_id:
        query["equipo_id"] = equipo_id
    if estado:
        query["estado"] = estado
    matches = await list_docs("matches", query)
    teams = {t["id"]: t["nombre"] for t in await list_docs("teams")}
    for m in matches:
        m["equipo_nombre"] = teams.get(m.get("equipo_id"), "—")
    return matches


@api_router.get("/matches/{match_id}")
async def get_match(match_id: str):
    return await get_doc("matches", match_id)


@api_router.put("/matches/{match_id}")
async def edit_match(match_id: str, match: Match):
    return await update_doc("matches", match_id, match.model_dump())


@api_router.delete("/matches/{match_id}")
async def remove_match(match_id: str):
    return await delete_doc("matches", match_id)


# ================= CALLUPS (Convocatorias) =================
class ConvocadoItem(BaseModel):
    player_id: str
    estado: str = "pendiente"  # pendiente, confirmado, no_puede
    motivo: Optional[str] = None


class Callup(BaseModel):
    match_id: str
    equipo_id: Optional[str] = None
    convocados: List[ConvocadoItem] = []
    hora_quedada: Optional[str] = None
    lugar_quedada: Optional[str] = None
    material: Optional[str] = None
    mensaje_familias: Optional[str] = None


@api_router.post("/callups")
async def create_callup(callup: Callup):
    return await insert_doc("callups", callup.model_dump())


@api_router.get("/callups")
async def get_callups():
    callups = await list_docs("callups")
    matches = {m["id"]: m for m in await list_docs("matches")}
    teams = {t["id"]: t["nombre"] for t in await list_docs("teams")}
    for c in callups:
        m = matches.get(c.get("match_id"), {})
        c["match"] = m
        c["equipo_nombre"] = teams.get(c.get("equipo_id"), "—")
        c["num_convocados"] = len(c.get("convocados", []))
    return callups


@api_router.get("/callups/{callup_id}")
async def get_callup(callup_id: str):
    c = await get_doc("callups", callup_id)
    players = {p["id"]: p for p in await list_docs("players")}
    for item in c.get("convocados", []):
        p = players.get(item["player_id"], {})
        item["nombre"] = f"{p.get('nombre','')} {p.get('apellidos','')}".strip()
        item["dorsal"] = p.get("dorsal")
        item["foto"] = p.get("foto")
    return c


@api_router.put("/callups/{callup_id}")
async def edit_callup(callup_id: str, callup: Callup):
    return await update_doc("callups", callup_id, callup.model_dump())


@api_router.delete("/callups/{callup_id}")
async def remove_callup(callup_id: str):
    return await delete_doc("callups", callup_id)


# ================= PAYMENTS =================
class Payment(BaseModel):
    player_id: Optional[str] = None
    concepto: Optional[str] = "Cuota temporada"
    importe_base: Optional[float] = 0
    descuento_hermano: Optional[float] = 0
    importe_final: Optional[float] = 0
    forma_pago: Optional[str] = None  # domiciliacion, transferencia, efectivo, bizum
    iban: Optional[str] = None
    iban_validado: bool = False
    estado: str = "pendiente"  # pendiente, pagado, parcial, devuelto
    fecha_pago: Optional[str] = None
    recibo_generado: bool = False
    observaciones: Optional[str] = None


@api_router.post("/payments")
async def create_payment(payment: Payment):
    data = payment.model_dump()
    base = data.get("importe_base") or 0
    desc = data.get("descuento_hermano") or 0
    data["importe_final"] = round(base - desc, 2)
    return await insert_doc("payments", data)


@api_router.get("/payments")
async def get_payments(estado: Optional[str] = None):
    query = {"estado": estado} if estado else {}
    payments = await list_docs("payments", query)
    players = {p["id"]: f"{p.get('nombre','')} {p.get('apellidos','')}".strip() for p in await list_docs("players")}
    for p in payments:
        p["player_nombre"] = players.get(p.get("player_id"), "—")
    return payments


@api_router.put("/payments/{payment_id}")
async def edit_payment(payment_id: str, payment: Payment):
    data = payment.model_dump()
    base = data.get("importe_base") or 0
    desc = data.get("descuento_hermano") or 0
    data["importe_final"] = round(base - desc, 2)
    return await update_doc("payments", payment_id, data)


@api_router.delete("/payments/{payment_id}")
async def remove_payment(payment_id: str):
    return await delete_doc("payments", payment_id)


# ================= AUTHORIZATIONS =================
class Authorization(BaseModel):
    player_id: Optional[str] = None
    tipo: str = "general"  # general, imagen, medica, desplazamientos, recogida, proteccion_datos
    persona_autorizada: Optional[str] = None
    dni_autorizada: Optional[str] = None
    firmante: Optional[str] = None
    fecha_firma: Optional[str] = None
    fecha_caducidad: Optional[str] = None
    estado: str = "pendiente"  # pendiente, firmada, caducada
    observaciones: Optional[str] = None


@api_router.post("/authorizations")
async def create_authorization(auth: Authorization):
    return await insert_doc("authorizations", auth.model_dump())


@api_router.get("/authorizations")
async def get_authorizations(estado: Optional[str] = None):
    query = {"estado": estado} if estado else {}
    auths = await list_docs("authorizations", query)
    players = {p["id"]: p for p in await list_docs("players")}
    for a in auths:
        p = players.get(a.get("player_id"), {})
        a["player_nombre"] = f"{p.get('nombre','')} {p.get('apellidos','')}".strip() or "—"
    return auths


@api_router.put("/authorizations/{auth_id}")
async def edit_authorization(auth_id: str, auth: Authorization):
    return await update_doc("authorizations", auth_id, auth.model_dump())


@api_router.delete("/authorizations/{auth_id}")
async def remove_authorization(auth_id: str):
    return await delete_doc("authorizations", auth_id)


# ================= SETTINGS / CONFIG =================
class Settings(BaseModel):
    club_nombre: Optional[str] = "Ikas-Txiki"
    club_logo: Optional[str] = None
    club_direccion: Optional[str] = None
    club_email: Optional[str] = None
    club_telefono: Optional[str] = None
    temporada_actual: Optional[str] = None
    temporadas: List[str] = []
    campos: List[str] = []
    entrenadores: List[str] = []
    cuota_base: Optional[float] = 0
    descuento_hermano: Optional[float] = 0


SETTINGS_ID = "global"


@api_router.get("/settings")
async def get_settings():
    doc = await db.settings.find_one({"id": SETTINGS_ID}, {"_id": 0})
    if not doc:
        default = Settings().model_dump()
        default["id"] = SETTINGS_ID
        default["categories"] = CATEGORIES
        await db.settings.insert_one(dict(default))
        return clean(default)
    doc["categories"] = CATEGORIES
    return doc


@api_router.put("/settings")
async def update_settings(settings: Settings):
    data = settings.model_dump()
    data["id"] = SETTINGS_ID
    await db.settings.update_one({"id": SETTINGS_ID}, {"$set": data}, upsert=True)
    return await get_settings()


@api_router.get("/categories")
async def get_categories():
    return CATEGORIES


@api_router.get("/compute-category")
async def api_compute_category(fecha_nacimiento: str):
    return {"categoria": compute_category(fecha_nacimiento)}


# ================= DASHBOARD =================
@api_router.get("/dashboard")
async def dashboard():
    players = await list_docs("players")
    matches = await list_docs("matches")
    payments = await list_docs("payments")
    auths = await list_docs("authorizations")

    activos = [p for p in players if p.get("estado") == "activo"]
    pendientes_doc = [p for p in players if p.get("estado_documental") != "completo"]
    nuevas_inscripciones = [p for p in players if p.get("nueva_incorporacion")]
    inscripciones_pendientes = [p for p in players if p.get("estado") in ("pendiente_documentacion", "en_prueba")]
    pagos_pendientes = [p for p in payments if p.get("estado") in ("pendiente", "parcial")]
    auth_pendientes = [a for a in auths if a.get("estado") == "pendiente"]

    today = date.today().isoformat()
    proximos_partidos = sorted(
        [m for m in matches if m.get("fecha") and m.get("fecha") >= today and m.get("estado") == "programado"],
        key=lambda m: (m.get("fecha"), m.get("hora") or "")
    )[:5]
    teams = {t["id"]: t["nombre"] for t in await list_docs("teams")}
    for m in proximos_partidos:
        m["equipo_nombre"] = teams.get(m.get("equipo_id"), "—")

    alertas = []
    if pagos_pendientes:
        alertas.append({"tipo": "pago", "mensaje": f"{len(pagos_pendientes)} pagos pendientes"})
    if pendientes_doc:
        alertas.append({"tipo": "doc", "mensaje": f"{len(pendientes_doc)} jugadores con documentación incompleta"})
    if auth_pendientes:
        alertas.append({"tipo": "auth", "mensaje": f"{len(auth_pendientes)} autorizaciones pendientes de firma"})

    return {
        "jugadores_activos": len(activos),
        "total_jugadores": len(players),
        "nuevas_inscripciones": len(nuevas_inscripciones),
        "inscripciones_pendientes": len(inscripciones_pendientes),
        "documentacion_pendiente": len(pendientes_doc),
        "pagos_pendientes": len(pagos_pendientes),
        "importe_pendiente": round(sum((p.get("importe_final") or 0) for p in pagos_pendientes), 2),
        "autorizaciones_pendientes": len(auth_pendientes),
        "proximos_partidos": proximos_partidos,
        "alertas": alertas,
    }


@api_router.get("/")
async def root():
    return {"message": "Ikas-Txiki Manager API"}


app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
