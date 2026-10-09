# ⚡ Autonomous Social Video Growth Agent (Meta Reels & YouTube Shorts)

> **Agente de software autónomo full-stack para generación diaria, publicación multicanal y análisis de crecimiento de videos verticales (9:16) con costo de infraestructura $0.**
> Diseñado para ejecutarse 100% en GitHub Actions y desplegar un Dashboard en tiempo real en GitHub Pages.

---

## 🌟 Resumen del Sistema

El agente resuelve el ciclo completo de creación y distribución de contenido corto viral:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        CICLO AUTÓNOMO DE CRECIMIENTO                   │
└────────────────────────────────────────────────────────────────────────┘
          │
          ▼
   [1. Growth Optimizer] ────► Analiza videos anteriores (tasa de engagement, ganchos)
          │                   y selecciona el guión y tema con mayor probabilidad viral.
          ▼
   [2. Video Engine]     ────► Sintetiza locución neural ultrarrealista (Edge-TTS) y
          │                   renderiza video 1080x1920 con cortes cada 3s y subtítulos.
          ▼
   [3. Multi-Publisher]  ────► Publica en paralelo en:
          │                   • YouTube Data API v3 (#Shorts, resumable upload)
          │                   • Meta Graph API v19.0 (Facebook Page Reels)
          ▼
   [4. Data & Analytics] ────► Consulta periódicamente vistas, likes, retención y shares;
          │                   actualiza `history.json` y `metrics.json`.
          ▼
   [5. Web Dashboard]    ────► Compila y sirve en GitHub Pages la interfaz en React + Vite
                              para monitoreo de métricas e ingresos de monetización.
```

---

## 📁 Estructura del Proyecto

```text
├── .github/
│   └── workflows/
│       ├── auto_publish.yml        # Workflow diario: creación, renderizado FFmpeg y subida
│       └── fetch_analytics.yml     # Consulta de métricas cada 12h y despliegue del Dashboard
├── bot/
│   ├── __init__.py
│   ├── video_engine.py             # Motor 9:16 vertical, audio TTS neural y kinetic captions
│   ├── uploader_youtube.py         # Subida a YouTube Data API v3 con OAuth2 refresh token
│   ├── uploader_facebook.py        # Subida a Facebook Reels vía Meta Graph API (3 fases)
│   ├── analytics_collector.py      # Extracción de métricas de YouTube y Facebook
│   ├── growth_optimizer.py         # Bucle de retroalimentación de temas y ganchos virales
│   ├── get_youtube_token.py        # Script auxiliar interactivo para obtener el Refresh Token
│   └── main.py                     # CLI y orquestador del pipeline
├── data/
│   ├── history.json                # Registro cronológico de videos, enlaces y estado
│   └── metrics.json                # Histórico de rendimiento (views, watch time, shares)
├── dashboard/                      # Dashboard React + Vite + Tailwind CSS + Recharts
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx          # Estado del bot y última sincronización
│   │   │   ├── MetricCard.jsx      # KPIs visuales con estilo glassmorphism y glows
│   │   │   ├── GrowthChart.jsx     # Gráficas interactivas con Recharts
│   │   │   ├── MonetizationTips.jsx# Seguimiento de metas monetizables y sugerencias IA
│   │   │   └── VideoTable.jsx      # Tabla de videos con enlaces directos a Shorts y Reels
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js              # Configuración con base path relativo para GitHub Pages
├── requirements.txt                # Dependencias Python
├── .env.example                    # Plantilla de variables de entorno
└── README.md
```

---

## 🚀 Guía de Configuración Paso a Paso (Costo $0)

Para operar el sistema de forma completamente autónoma sin pagar servidores, utilizaremos los runners gratuitos de **GitHub Actions** (2,000 minutos mensuales gratis) y **GitHub Pages**.

### Paso 1: Configurar YouTube Data API v3 (Gratis)

1. Ve a [Google Cloud Console](https://console.cloud.google.com/) e inicia sesión con tu cuenta de Google.
2. Crea un nuevo proyecto (ej. `Social-Video-Bot`).
3. Ve a **APIs & Services > Library**, busca **YouTube Data API v3** y haz clic en **Enable**.
4. Ve a **APIs & Services > OAuth consent screen**:
   * Selecciona **External** y pulsa **Create**.
   * Completa los campos básicos (Nombre de app, correo).
   * En la pestaña **Test Users**, añade tu propia dirección de correo de Google (la dueña del canal de YouTube).
5. Ve a **APIs & Services > Credentials**:
   * Clic en **Create Credentials > OAuth client ID**.
   * Application type: **Desktop app**.
   * Haz clic en **Create**. Guarda tu `Client ID` y `Client Secret`.
6. En tu terminal local, genera el `Refresh Token` permanente ejecutando:
   ```bash
   pip install -r requirements.txt
   python bot/get_youtube_token.py
   ```
   * Se abrirá el navegador para autorizar la aplicación.
   * La consola te imprimirá tu `YT_REFRESH_TOKEN`. ¡Guárdalo!

---

### Paso 2: Configurar Meta Graph API para Facebook Reels (Gratis)

1. Asegúrate de tener una **Página de Facebook** pública donde se publicarán los Reels.
2. Entra a [Meta for Developers](https://developers.facebook.com/) y haz clic en **My Apps > Create App**.
3. Selecciona el caso de uso **Other** > Tipo **Business** y nómbrala (ej. `ReelsAutoPublisher`).
4. Ve al [Graph API Explorer](https://developers.facebook.com/tools/explorer/):
   * Selecciona tu app en el selector superior derecho.
   * En **User or Page**, selecciona tu **Página de Facebook**.
   * En **Permissions**, añade los siguientes permisos:
     * `pages_manage_posts`
     * `pages_read_engagement`
     * `pages_show_list`
   * Clic en **Generate Access Token** y acepta los permisos.
5. Para que el token **no expire**, ve a [Access Token Debugger](https://developers.facebook.com/tools/debug/accesstoken/), pega el token y pulsa **Extend Access Token** para obtener el token de larga duración de la página.
6. Copia tu `FB_PAGE_ID` (el ID numérico de tu página) y el `FB_PAGE_ACCESS_TOKEN`.

---

### Paso 3: Configurar los Secrets en tu Repositorio de GitHub

En tu repositorio de GitHub:
1. Ve a **Settings > Secrets and variables > Actions > New repository secret**.
2. Añade los siguientes 5 secretos:

| Nombre del Secret | Descripción |
| :--- | :--- |
| `YT_CLIENT_ID` | Tu Client ID de Google Cloud |
| `YT_CLIENT_SECRET` | Tu Client Secret de Google Cloud |
| `YT_REFRESH_TOKEN` | El refresh token generado con `bot/get_youtube_token.py` |
| `FB_PAGE_ID` | El ID numérico de tu Página de Facebook |
| `FB_PAGE_ACCESS_TOKEN` | Token de acceso de larga duración para la página |

3. En **Settings > Actions > General > Workflow permissions**, marca:
   * **Read and write permissions**
   * Marca la casilla **Allow GitHub Actions to create and approve pull requests**.
4. En **Settings > Pages > Build and deployment**:
   * En **Source**, selecciona **GitHub Actions**.

---

## 💻 Ejecución y Pruebas Locales

Puedes probar el sistema de inmediato en tu computadora, incluso sin credenciales activas gracias al modo `--dry-run`:

### 1. Instalar dependencias
```bash
# Python
python -m venv venv
# En Windows:
.\venv\Scripts\activate
# En Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Probar la generación de video en modo simulación (Dry Run)
```bash
# Genera el video MP4 vertical con subtítulos y audio TTS neural sin subir a APIs
python bot/main.py --mode publish --dry-run
```
El video generado aparecerá en la carpeta `output/`.

### 3. Probar con un tema personalizado
```bash
python bot/main.py --mode publish --topic "3 Consejos de Productividad Extrema" --dry-run
```

### 4. Recolectar analíticas
```bash
python bot/main.py --mode analytics
```

### 5. Iniciar el Dashboard en Desarrollo
```bash
cd dashboard
npm install
npm run dev
```
Abre `http://localhost:5173` en tu navegador para ver la interfaz interactiva.

---

## ⚙️ Automatización en GitHub Actions

El repositorio incluye dos flujos de trabajo preconfigurados:

1. **`auto_publish.yml`**:
   * Se ejecuta diariamente a las **14:00 UTC** (puedes ajustar el `cron`).
   * Incluye soporte para ejecución manual desde la pestaña **Actions > Auto Publish > Run workflow**, donde puedes ingresar un tema personalizado y elegir si ejecutar en modo real o dry-run.
   * Renderiza el video, lo sube a YouTube y Facebook, y actualiza el historial en `data/history.json`.

2. **`fetch_analytics.yml`**:
   * Se ejecuta cada **12 horas** y automáticamente después de cada publicación.
   * Extrae vistas, likes, comentarios e impresiones de ambos canales.
   * Alimenta el motor de optimización de crecimiento (`growth_optimizer.py`).
   * Compila el dashboard de React y lo despliega automáticamente en **GitHub Pages**.

---

## 🧠 Algoritmo de Viralidad y Optimización

El motor implementa las mejores prácticas probadas en YouTube Shorts y Meta Reels:

1. **Fórmula Hook-Value-CTA**:
   * **0 a 3s (Gancho visual y sonoro):** Insignia de alta urgencia en rojo/amarillo con texto contrastante para maximizar la retención del swipe.
   * **Cuerpo (Ritmo y Pacing):** Cortes visuales o cambios de escena cada 2.5 a 3.5 segundos con numeración `#1, #2, #3` para mantener la atención del espectador.
   * **Final (CTA enfocado en el algoritmo):** Preguntas directas invitando al debate en comentarios (la señal de mayor peso algorítmico en Reels).
2. **Subtítulos Cinematográficos:** Tipografía negrita de alta visibilidad en amarillo y blanco con borde negro exterior y sombra paralela.
3. **Bucle de Aprendizaje:** Los temas y formatos con métricas superiores a la media histórica reciben mayor peso ponderado en la siguiente selección automática.

---

## 📊 Métricas y Monetización en el Dashboard

El Dashboard permite monitorear:
* **Progreso hacia el Programa de Socios de YouTube:** Meta de 10,000,000 de vistas en Shorts en 90 días.
* **Bono de Desempeño de Meta Reels:** Progreso hacia 500,000 reproducciones.
* **Tasa de Interacción Consolidada:** `(Likes + Comentarios + Compartidos) / Vistas`.
* **Desglose comparativo por plataforma:** YouTube Shorts vs Facebook Reels.
* **Acceso directo:** Botones para abrir cada video publicado en su respectiva plataforma.

---

## 🛡️ Licencia

Distribuido bajo la licencia MIT. Libre para uso personal o comercial.
