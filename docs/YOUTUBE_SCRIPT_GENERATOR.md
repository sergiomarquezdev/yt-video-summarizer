# YouTube Script Generator

Sistema inteligente que genera guiones optimizados para YouTube aprendiendo de videos exitosos en tiempo real.

## 📋 Tabla de Contenidos

- [¿Qué es?](#qué-es)
- [¿Cómo funciona?](#cómo-funciona)
- [Instalación](#instalación)
- [Uso Rápido](#uso-rápido)
- [Workflow Completo](#workflow-completo)
- [Configuración](#configuración)
- [Ejemplos](#ejemplos)
- [Troubleshooting](#troubleshooting)
- [Arquitectura](#arquitectura)

## ¿Qué es?

YouTube Script Generator es una herramienta que:

1. **Busca** los videos más exitosos sobre un tema
2. **Analiza** sus patrones (hooks, estructura, CTAs, vocabulario)
3. **Sintetiza** las mejores prácticas identificadas
4. **Genera** un guión profesional aplicando esos patrones

**Resultado**: Un guión de YouTube optimizado basado en datos reales de videos exitosos.

## ¿Cómo funciona?

### Pipeline Completo (6 Fases)

```
Idea del usuario
    ↓
1. Query Optimization (Gemini)
    ↓ "FastAPI tutorial Python REST API"
2. YouTube Search (yt-dlp)
    ↓ Top 10-15 videos por views/duración
3. Batch Processing
    ├─ Download (yt-dlp)
    └─ Transcribe (Whisper CUDA)
    ↓ 10-15 transcripciones completas
4. Pattern Analysis (Gemini)
    ├─ Hooks efectivos
    ├─ Estructura óptima
    ├─ CTAs estratégicos
    └─ Vocabulario clave
    ↓ 10-15 análisis individuales
5. Pattern Synthesis (Gemini)
    ├─ Top 10 hooks
    ├─ Mejores CTAs
    ├─ Técnicas destacables
    └─ Keywords SEO
    ↓ 1 síntesis consolidada
6. Script Generation (Gemini)
    └─ Guión completo con timestamps
```

## Instalación

### Requisitos Previos

- Python 3.9+
- FFmpeg (para procesamiento de audio)
- GPU CUDA (opcional, mejora velocidad de transcripción)
- API Key de Google Gemini

### Instalación de Dependencias

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/yt-video-summarizer.git
cd yt-video-summarizer

# Instalar dependencias con UV (recomendado)
uv sync --extra dev

# O con pip tradicional
pip install -r requirements.txt
```

### Configuración de API Keys

Crea un archivo `.env` en la raíz del proyecto:

```bash
# .env
GOOGLE_API_KEY=tu_api_key_de_gemini
GEMINI_PRO_MODEL=gemini-2.0-flash-exp

# Whisper configuration (opcional)
WHISPER_MODEL_NAME=base
WHISPER_DEVICE=cuda
```

**Obtener API Key de Gemini:**
1. Ve a [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Crea un nuevo proyecto
3. Genera una API key
4. Copia la key al archivo `.env`

## Uso Rápido

### Comando Básico

```bash
uv run python -m yt_transcriber.cli generate-script \
  --idea "crear una API REST con FastAPI desde cero"
```

### Con Opciones Personalizadas

```bash
uv run python -m yt_transcriber.cli generate-script \
  --idea "tutorial de Python para principiantes" \
  --max-videos 15 \
  --duration 12 \
  --min-duration 8 \
  --max-duration 20 \
  --style educational
```

### Argumentos Disponibles

| Argumento | Descripción | Default | Ejemplo |
|-----------|-------------|---------|---------|
| `--idea` (requerido) | Idea del video | - | `"crear API REST con FastAPI"` |
| `--max-videos` | Número de videos a analizar | 10 | `15` |
| `--duration` | Duración objetivo del guión (min) | 10 | `12` |
| `--min-duration` | Duración mínima de videos a buscar | 5 | `8` |
| `--max-duration` | Duración máxima de videos a buscar | 45 | `20` |
| `--style` | Preferencia de estilo | None | `educational`, `entertaining` |

## Workflow Completo

### 1. Query Optimization

El sistema optimiza tu idea para la búsqueda de YouTube:

**Input**: `"crear proyecto FastAPI"`
**Output**: `"FastAPI Python proyecto tutorial REST API beginners"`

- Usa Gemini para expandir keywords
- Elimina stopwords
- Añade términos relacionados

### 2. YouTube Search

Busca videos exitosos usando criterios optimizados:

- **Filtros**: Duración (5-45 min), Views (descendente)
- **Ranking**: Quality score ponderado
- **Salida**: Top N videos ordenados por efectividad

### 3. Batch Processing

Descarga y transcribe videos en paralelo:

- **Download**: Extrae audio con yt-dlp
- **Transcribe**: Whisper con CUDA (23 seg/video en RTX 3060)
- **Cleanup**: Elimina archivos temporales automáticamente

### 4. Pattern Analysis

Analiza cada video individualmente con Gemini:

**Patrones extraídos:**
- **Hook**: Primeros 10-30 segundos (texto, tipo, efectividad)
- **Estructura**: Secciones con timestamps
- **CTAs**: Calls-to-action (tipo, posición, texto)
- **Vocabulario**: Términos técnicos, frases comunes
- **Técnicas**: Storytelling, ejemplos, analogías
- **SEO**: Keywords en título y descripción

### 5. Pattern Synthesis

Consolida análisis en un documento de mejores prácticas:

**Synthesis incluye:**
- Top 10 hooks más efectivos
- Estructura óptima (promedio ponderado por views)
- CTAs más frecuentes y sus posiciones
- Top 20 términos técnicos del nicho
- Técnicas destacables de videos top
- Keywords SEO más comunes

### 6. Script Generation

Genera guión completo aplicando patrones:

**El guión incluye:**
- Hook optimizado (basado en top hooks)
- Estructura con timestamps `[MM:SS]`
- 2-3 CTAs en posiciones estratégicas
- Vocabulario del nicho
- SEO completo (título, descripción, tags)

## Configuración

### Variables de Entorno

```bash
# Gemini API
GOOGLE_API_KEY=your_key_here
GEMINI_PRO_MODEL=gemini-2.0-flash-exp

# Whisper
WHISPER_MODEL_NAME=base  # tiny, base, small, medium, large
WHISPER_DEVICE=cuda      # cuda, cpu

# Logging
LOG_LEVEL=INFO           # DEBUG, INFO, WARNING, ERROR

# Directories (auto-created)
TEMP_DIR=temp_files
OUTPUT_DIR=output_transcripts
```

### Modelos Whisper

| Modelo | Velocidad | Precisión | VRAM | Uso Recomendado |
|--------|-----------|-----------|------|-----------------|
| `tiny` | ⚡⚡⚡ | ⭐⭐ | ~1GB | Pruebas rápidas |
| `base` | ⚡⚡ | ⭐⭐⭐ | ~1GB | **Default recomendado** |
| `small` | ⚡ | ⭐⭐⭐⭐ | ~2GB | Mejor precisión |
| `medium` | 🐌 | ⭐⭐⭐⭐⭐ | ~5GB | Producción alta calidad |
| `large` | 🐌🐌 | ⭐⭐⭐⭐⭐ | ~10GB | Máxima precisión |

## Ejemplos

### Ejemplo 1: Tutorial de Programación

```bash
uv run python -m yt_transcriber.cli generate-script \
  --idea "tutorial de FastAPI para principiantes" \
  --max-videos 12 \
  --duration 15 \
  --style educational
```

**Output esperado:**
- Guión de 15 minutos (~2,250 palabras)
- Hook tipo "pregunta" o "promesa"
- 3-4 secciones principales
- 2-3 CTAs (like, subscribe, comment)
- Vocabulario técnico: FastAPI, async, Pydantic, etc.

### Ejemplo 2: Tutorial Rápido

```bash
uv run python -m yt_transcriber.cli generate-script \
  --idea "configurar entorno Python en 5 minutos" \
  --max-videos 8 \
  --duration 6 \
  --min-duration 3 \
  --max-duration 10
```

**Output esperado:**
- Guión corto de 6 minutos (~900 palabras)
- Hook directo y rápido
- 2-3 secciones concisas
- Ritmo rápido, paso a paso

### Ejemplo 3: Contenido Entretenido

```bash
uv run python -m yt_transcriber.cli generate-script \
  --idea "los errores más comunes en Python" \
  --max-videos 10 \
  --duration 12 \
  --style entertaining
```

**Output esperado:**
- Guión entretenido (~1,800 palabras)
- Hook con estadística o dato sorprendente
- Tono más casual
- Storytelling y ejemplos divertidos

## Troubleshooting

### Error: "No videos found for query"

**Causa**: Los filtros de duración son demasiado restrictivos.

**Solución**:
```bash
# Amplía el rango de duración
--min-duration 3 --max-duration 60
```

### Error: "CUDA not available"

**Causa**: PyTorch no detecta GPU CUDA.

**Solución**:
```bash
# Reinstala PyTorch con CUDA
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128 --force-reinstall

# O usa CPU (más lento)
# En .env: WHISPER_DEVICE=cpu
```

### Error: "YouTube search timed out"

**Causa**: yt-dlp tardó >60 segundos.

**Solución**:
```bash
# Reduce max-videos
--max-videos 5

# O verifica conexión de red
```

### Error: "Gemini API quota exceeded"

**Causa**: Límite de requests gratuitos alcanzado.

**Solución**:
- Espera 24 horas (reset diario)
- Upgrade a plan pago de Gemini API
- Reduce `--max-videos` para menos API calls

### Advertencia: "Synthesis quality may be low"

**Causa**: Pocos videos analizados (<5).

**Solución**:
```bash
# Aumenta max-videos
--max-videos 15
```

## Arquitectura

### Módulos del Sistema

```
youtube_script_generator/
├── query_optimizer.py      # Optimiza búsqueda con Gemini
├── youtube_searcher.py     # Busca videos con yt-dlp
├── batch_processor.py      # Download + transcribe en batch
├── pattern_analyzer.py     # Analiza patrones de cada video
├── synthesizer.py          # Sintetiza múltiples análisis
├── script_generator.py     # Genera guión final
└── models.py               # Dataclasses compartidas
```

### Dataclasses Principales

#### YouTubeVideo
```python
@dataclass
class YouTubeVideo:
    video_id: str
    title: str
    url: str
    duration_seconds: int
    view_count: int
    upload_date: str
    channel: str

    @property
    def quality_score(self) -> float:
        # Views (40%) + Duration (20%) + Recency (20%) + Completeness (20%)
```

#### VideoAnalysis
```python
@dataclass
class VideoAnalysis:
    video: YouTubeVideo

    # Structure
    hook_start: int
    hook_end: int
    hook_text: str
    hook_type: str  # question, statistic, promise, problem
    sections: list[dict]

    # CTAs
    ctas: list[dict]  # [{text, timestamp, type}]

    # Vocabulary
    technical_terms: list[str]
    common_phrases: list[str]

    # SEO
    title_keywords: list[str]
    estimated_tags: list[str]
```

#### PatternSynthesis
```python
@dataclass
class PatternSynthesis:
    topic: str
    num_videos_analyzed: int

    # Top patterns (weighted by quality_score)
    top_hooks: list[dict]
    optimal_structure: dict
    effective_ctas: list[dict]
    key_vocabulary: dict
    notable_techniques: list[dict]
    seo_patterns: dict

    # Report
    markdown_report: str
```

#### GeneratedScript
```python
@dataclass
class GeneratedScript:
    user_idea: str
    script_markdown: str
    estimated_duration_minutes: int
    word_count: int

    # SEO
    seo_title: str
    seo_description: str
    seo_tags: list[str]

    # Quality
    estimated_quality_score: int  # 1-100
```

### Flujo de Datos

```
User Input (idea)
    ↓
QueryOptimizer → OptimizedQuery
    ↓
YouTubeSearcher → list[YouTubeVideo]
    ↓
BatchProcessor → list[VideoTranscript]
    ↓
PatternAnalyzer → list[VideoAnalysis]
    ↓
PatternSynthesizer → PatternSynthesis
    ↓
ScriptGenerator → GeneratedScript
    ↓
Output Files (.md)
```

## Costes Estimados

### Por Ejecución (10 videos)

| Fase | API Calls | Tokens | Coste (Gemini 2.0 Flash) |
|------|-----------|--------|--------------------------|
| Query Optimization | 1 | ~500 | $0.001 |
| Pattern Analysis | 10 | ~50,000 | $0.050 |
| Synthesis | 1 | ~10,000 | $0.010 |
| Script Generation | 1 | ~5,000 | $0.005 |
| **TOTAL** | **13** | **~65,500** | **~$0.066** |

**Nota**: Con tier gratuito de Gemini (50 requests/día), puedes generar ~3 guiones/día gratis.

### Tiempo de Ejecución (GPU RTX 3060)

| Fase | Tiempo/Video | Tiempo Total (10 videos) |
|------|--------------|--------------------------|
| Download | ~15s | ~2.5 min |
| Transcribe | ~23s | ~4 min |
| Analysis | ~5s | ~1 min |
| Synthesis | - | ~20s |
| Generation | - | ~15s |
| **TOTAL** | - | **~8-10 min** |

## Roadmap Futuro

### Mejoras Planificadas

- [ ] Soporte para múltiples idiomas
- [ ] Cache de análisis para reutilización
- [ ] Interfaz web (Streamlit/Gradio)
- [ ] Exportación a Google Docs
- [ ] Generación de thumbnails sugeridos
- [ ] Análisis de sentimiento en comentarios
- [ ] Predicción de performance (views esperadas)

### Contribuciones

¡Pull requests bienvenidos! Ver [CONTRIBUTING.md](../CONTRIBUTING.md) para guidelines.

## Licencia

MIT License - Ver [LICENSE](../LICENSE) para detalles.

## Soporte

- **Issues**: [GitHub Issues](https://github.com/tu-usuario/yt-video-summarizer/issues)
- **Discusiones**: [GitHub Discussions](https://github.com/tu-usuario/yt-video-summarizer/discussions)
- **Email**: tu-email@example.com

---

**¿Preguntas?** Consulta primero la sección [Troubleshooting](#troubleshooting) o abre un issue en GitHub.
