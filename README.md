# Análisis de Imagen - Botmaker

API de FastAPI para analizar imágenes usando OpenAI GPT-4 Vision.

## Despliegue en Railway

### Opción 1: Despliegue automático desde GitHub

1. **Conecta tu repositorio a Railway:**
   - Ve a [Railway](https://railway.app)
   - Crea un nuevo proyecto
   - Conecta tu repositorio de GitHub

2. **Configura las variables de entorno en Railway:**
   - `APP_SECRET`: Tu secreto para autenticación
   - `OPENAI_API_KEY`: Tu clave de API de OpenAI
   - `OPENAI_MODEL`: gpt-4o-mini (opcional)

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
# Copia el archivo de ejemplo
cp .env.example .env

# Edita .env con tus valores reales
```

3. Ejecuta el servidor:
```bash
python main.py
```

## Variables de entorno requeridas

- `APP_SECRET`: Secreto para autenticación de la API
- `OPENAI_API_KEY`: Clave de API de OpenAI
- `OPENAI_MODEL`: Modelo a usar (opcional, por defecto: gpt-4o-mini)

## Uso

### Endpoint: POST /analyze-image

**Headers:**
- `Authorization: Bearer <APP_SECRET>`

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
