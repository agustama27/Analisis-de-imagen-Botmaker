import os, json, base64
from typing import Any, Dict, List, Optional
import httpx
from fastapi import FastAPI, Header, HTTPException, Request
from openai import OpenAI

APP_SECRET = os.getenv("APP_SECRET", "")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # visión
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

def ensure_auth(auth_header: Optional[str]):
    token = (auth_header or "").replace("Bearer ", "").strip()
    if not APP_SECRET or token != APP_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")

def find_last_image_url(payload: Any) -> Optional[str]:
    """Busca la última imagen recorriendo estructuras típicas de historial."""
    data = json.loads(payload) if isinstance(payload, str) else payload
    root = data if isinstance(data, list) else data.get("messages") or data.get("history") \
        or data.get("entries") or data.get("items") or []

    stack: List[Any] = list(root)
    flat: List[Any] = []
    while stack:
        n = stack.pop()
        if n is None: 
            continue
        if isinstance(n, list):
            stack.extend(n)
            continue
        flat.append(n)
        for k in ["attachments","attachment","media","files","file","items","children","payload"]:
            v = n.get(k) if isinstance(n, dict) else None
            if isinstance(v, list): stack.extend(v)
            elif isinstance(v, dict): stack.append(v)

    def is_img_url(u: Any) -> bool:
        if not isinstance(u, str): return False
        import re
        return re.search(r"(https?://[^\s]+)\.(png|jpe?g|webp|gif)(\?|$)", u, re.I) is not None

    def looks_image_mime(t: Any) -> bool:
        return isinstance(t, str) and t.lower().startswith("image/")

    for m in reversed(flat):
        if not isinstance(m, dict): 
            continue
        urls = [m.get("imageUrl"), m.get("url"), m.get("mediaUrl"), m.get("fileUrl"),
                m.get("downloadUrl")]
        media = m.get("media") or {}
        attach = m.get("attachment") or {}
        urls += [media.get("url"), attach.get("url")]

        atts = m.get("attachments") or []
        for a in atts:
            if isinstance(a, dict):
                urls += [a.get("url"), a.get("downloadUrl"), a.get("mediaUrl")]
        files = m.get("files") or []
        for f in files:
            if isinstance(f, dict):
                urls += [f.get("url"), f.get("downloadUrl")]

        first = next((u for u in urls if u), None)
        mime = m.get("mimeType") or m.get("contentType") or media.get("type") or attach.get("contentType")

        if first and (is_img_url(first) or looks_image_mime(mime) or m.get("type") == "image" or m.get("messageType") == "image"):
            return first
    return None

async def to_image_part(image_url: str) -> Dict[str, Any]:
    # Si es pública, pásala directo (formato requerido por la API)
    if image_url.startswith("http://") or image_url.startswith("https://"):
        return {"type": "image_url", "image_url": {"url": image_url}}
    # Si fuera una ruta no pública, intenta descargar y embebé como data URL
    async with httpx.AsyncClient(timeout=10.0) as client_http:
        resp = await client_http.get(image_url)
        resp.raise_for_status()
        ct = resp.headers.get("content-type", "image/jpeg")
        b64 = base64.b64encode(resp.content).decode("utf-8")
        return {"type": "image_url", "image_url": {"url": f"data:{ct};base64,{b64}"}}

@app.post("/analyze-image")
async def analyze_image(request: Request, authorization: Optional[str] = Header(None)):
    ensure_auth(authorization)
    body = await request.json()
    desarrollo = body.get("desarrollo_historial") or body.get("desarrollo_json")
    if not desarrollo:
        raise HTTPException(status_code=400, detail="Falta 'desarrollo_historial' o 'desarrollo_json'.")

    last_url = find_last_image_url(desarrollo)
    if not last_url:
        raise HTTPException(status_code=422, detail="No se encontró una imagen en el historial.")

    image_part = await to_image_part(last_url)

    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "summary":   {"type": "string", "description": "Resumen breve en español de lo que se ve."},
            "ocr_text":  {"type": "string", "description": "Texto detectado (si existe)."},
            "labels":    {"type": "array", "items": {"type": "string"}, "description": "Etiquetas relevantes (máx 8)."},
            "safety":    {"type": "string", "enum": ["ok","sensible"], "description": "Marca si parece sensible."}
        },
        "required": ["summary"]
    }

    prompt = "Analiza la imagen. Devuelve JSON con: summary, ocr_text (si hay), labels (máx 8), safety ('ok' o 'sensible'). Sé preciso y conciso."

    # Chat Completions con imagen + Structured Outputs (json_schema)
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Eres un asistente experto en visión por computadora y OCR."},
            {"role": "user", "content": [
                {"type": "text", "text": prompt},
                image_part
            ]}
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "VisionSchema", "schema": schema, "strict": True}
        },
        temperature=0.2
    )

    content = resp.choices[0].message.content or "{}"
    analysis = json.loads(content)

    return {
        "ok": True,
        "model": MODEL,
        "imageUrl": last_url,
        "analysis": analysis
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)