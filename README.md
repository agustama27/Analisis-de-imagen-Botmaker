# Análisis de Imagen - Botmaker

API de FastAPI para analizar imágenes usando OpenAI GPT-4 Vision.

## Despliegue en Railway

### Opción 1: Despliegue automático desde GitHub

1. **Conecta tu repositorio a Railway:**
   - Ve a [Railway](https://railway.app)
   - Crea un nuevo proyecto
   - Conecta tu repositorio de GitHub

2. **Configura las variables de entorno en Railway:**
   - Ve a la pestaña "Variables" de tu proyecto
   - Agrega estas variables:
   
   | Variable | Valor | Requerida | Descripción |
   |----------|-------|-----------|-------------|
   | `OPENAI_API_KEY` | `sk-...` | ✅ **SÍ** | Tu clave de API de OpenAI |
   | `OPENAI_MODEL` | `gpt-4o-mini` | ✅ **SÍ** | Modelo a usar |
   | `APP_SECRET` | Cualquier valor | ❌ No | Autenticación (deshabilitada) |

3. **Railway detectará automáticamente:**
   - `requirements.txt` para las dependencias
   - `main.py` como punto de entrada
   - Puerto desde la variable `PORT`

### Opción 2: Despliegue local para testing

1. Instala las dependencias:
```bash
pip install -r requirements.txt
```

2. Configura las variables de entorno:
```bash
# En Windows PowerShell
$env:OPENAI_API_KEY="sk-tu-clave-aqui"
$env:OPENAI_MODEL="gpt-4o-mini"

# En Linux/Mac
export OPENAI_API_KEY="sk-tu-clave-aqui"
export OPENAI_MODEL="gpt-4o-mini"
```

3. Ejecuta el servidor:
```bash
python main.py
```

## Variables de entorno requeridas

- `OPENAI_API_KEY`: Clave de API de OpenAI (requerida)
- `OPENAI_MODEL`: Modelo a usar (requerida)
- `APP_SECRET`: Secreto para autenticación (opcional - deshabilitada temporalmente)

## Uso

### Endpoint: POST /analyze-image

**Headers:**
- `Authorization: Bearer <APP_SECRET>` (Opcional - autenticación deshabilitada)

**Body:**
```json
{
  "desarrollo_historial": {
    "messages": [
      {
        "imageUrl": "https://ejemplo.com/imagen.jpg"
      }
    ]
  }
}
```

**Respuesta:**
```json
{
  "ok": true,
  "model": "gpt-4o-mini",
  "imageUrl": "https://ejemplo.com/imagen.jpg",
  "analysis": {
    "summary": "Descripción de la imagen",
    "ocr_text": "Texto detectado",
    "labels": ["etiqueta1", "etiqueta2"],
    "safety": "ok"
  }
}
```
