# Implementation Plan: YouTube-Powered Script Generator

**Created**: 2025-01-03
**Status**: 🔄 Planning Phase
**Owner**: Planner
**Estimated Effort**: 15-18 hours
**Expected Quality**: 90-95/100

---

## Background and Motivation

### Problem Statement

Los creadores de contenido necesitan crear guiones de alta calidad para YouTube, pero:

- No saben qué estructura funciona mejor en su nicho
- No conocen los hooks más efectivos
- No tienen referencias actuales de videos exitosos
- Crear guiones desde cero consume mucho tiempo

### The Insight

En lugar de usar un RAG estático con patrones antiguos, **analizar dinámicamente los videos MÁS EXITOSOS del tema exacto** que el usuario quiere crear, y usar esos patrones para generar un guión optimizado.

### Goals

Crear un sistema que:

1. Reciba una idea de video del usuario
2. Encuentre los 15 videos más exitosos sobre ese tema en YouTube
3. Transcriba y analice todos esos videos
4. Extraiga patrones y mejores prácticas
5. Sintetice toda la información en un documento de referencia
6. Genere un guión optimizado usando esos patrones reales

### Success Criteria

- ✅ Genera guiones de calidad 90-95/100
- ✅ Proceso completo en <15 minutos
- ✅ Coste <0.20€ por guión
- ✅ Output Markdown legible y accionable
- ✅ Síntesis preserva información crítica
- ✅ Código testeable (>70% coverage)

---

## Key Challenges and Analysis

### Technical Challenges

#### 1. **YouTube Search Sin API Limits**

**Desafío**: YouTube Data API tiene límite de 100 búsquedas/día
**Solución**: Usar yt-dlp con `--flat-playlist` para scraping inteligente
**Ventajas**:

- Sin límites de cuota
- Más metadata (views, likes, duración)
- Ya instalado como dependencia
- Gratis completamente

#### 2. **Query Optimization**

**Desafío**: User input "crear proyecto con FastAPI en Python" tiene palabras irrelevantes
**Solución**: Gemini extrae keywords optimizadas: "FastAPI Python proyecto tutorial REST API"
**Coste**: ~0.002€ por optimización
**Beneficio**: Resultados más relevantes (+20% calidad estimada)

#### 3. **Batch Transcription Performance**

**Desafío**: Transcribir 15 videos de 15 min cada uno puede tardar mucho
**Solución**:

- Usar CUDA para Whisper (18 seg/video vs 3 min CPU)
- Procesamiento paralelo con asyncio (opcional Phase 2)
  **Tiempo estimado**: 5-7 minutos con CUDA secuencial

#### 4. **Synthesis Without Information Loss**

**Desafío**: Sintetizar 15 análisis sin perder detalles importantes
**Solución**: Prompt estructurado que categoriza información
**Categorías**: Hooks, Estructura, CTAs, Vocabulario, Técnicas, SEO
**Validación**: Verificar que síntesis mantiene top patterns de cada categoría

#### 5. **Weighting by Video Quality**

**Desafío**: No todos los videos tienen la misma calidad
**Solución**: Usar metadata de yt-dlp para ponderar
**Métricas**:

- View count (peso 40%)
- Video duration (peso 20% - más cercano a target mejor)
- Upload recency (peso 20% - más reciente mejor)
- Likes ratio (peso 20% - si disponible)

---

## High-level Task Breakdown

### Phase 0: Setup & Configuration (1 hour) ⏳

**Responsible**: Executor
**Dependencies**: None

**Subtasks**:

- [ ] Instalar `google-generativeai` dependency
- [ ] Configurar `GOOGLE_API_KEY` en `.env` y `config.py`
- [ ] Actualizar `pyproject.toml` con nueva dependencia
- [ ] Crear estructura `youtube_script_generator/`
- [ ] Verificar yt-dlp funciona con `--flat-playlist`
- [ ] Documentar setup en README

**Success Criteria**:

- `uv sync` instala google-generativeai sin errores
- yt-dlp puede buscar videos sin descargar
- Gemini API key válida y funcional
- Estructura de carpetas creada

**Tests Required**:

- `test_setup_gemini_api.py`: Verificar API key válida
- `test_ytdlp_search.py`: Verificar búsqueda sin download

---

### Phase 1: Query Optimizer (2 hours) ⏳

**Responsible**: Executor
**Dependencies**: Phase 0

**Subtasks**:

- [ ] Crear `youtube_script_generator/query_optimizer.py`
- [ ] Función `optimize_search_query(user_input: str) -> str`
- [ ] Prompt estructurado para extracción de keywords
- [ ] Fallback a query original si Gemini falla
- [ ] Logging de optimización (original → optimizada)
- [ ] Validación: keywords no vacías

**Success Criteria**:

- Extrae keywords relevantes eliminando stopwords
- Añade sinónimos útiles (tutorial, guide, proyecto)
- Falla gracefully si Gemini no disponible
- Tiempo <3 segundos por optimización

**Tests Required** (4 tests):

1. `test_optimize_query_success` - Query válida optimizada
2. `test_optimize_query_removes_stopwords` - Elimina "con", "en", "de"
3. `test_optimize_query_adds_synonyms` - Añade términos relevantes
4. `test_optimize_query_fallback` - Usa original si falla

**Input/Output Examples**:

```python
Input:  "crear proyecto con FastAPI en Python"
Output: "FastAPI Python proyecto tutorial REST API"

Input:  "cómo hacer deploy de app React en Vercel"
Output: "React Vercel deploy production tutorial"

Input:  "mejores prácticas de testing en Node.js"
Output: "Node.js testing best practices unit integration"
```

---

### Phase 2: YouTube Searcher (3 hours) ⏳

**Responsible**: Executor
**Dependencies**: Phase 1

**Subtasks**:

- [ ] Crear `youtube_script_generator/youtube_searcher.py`
- [ ] Dataclass `YouTubeVideo` (id, title, url, duration, views, upload_date)
- [ ] Función `search_youtube_videos(query, max_results, filters)`
- [ ] Integración con yt-dlp `--flat-playlist --dump-json`
- [ ] Parseo de JSON output de yt-dlp
- [ ] Filtros: duración (10-30 min), idioma (español/inglés)
- [ ] Ordenamiento por views (descendente)
- [ ] Manejo de timeouts y errores

**Success Criteria**:

- Busca y retorna top 15 videos en <30 segundos
- Filtra por duración correctamente
- Extrae metadata completa (views, duration, date)
- Maneja errores de red/timeout gracefully

**Tests Required** (6 tests):

1. `test_search_youtube_success` - Búsqueda válida retorna videos
2. `test_search_youtube_duration_filter` - Filtra por duración min/max
3. `test_search_youtube_max_results` - Respeta límite de resultados
4. `test_search_youtube_metadata` - Extrae todos los campos
5. `test_search_youtube_timeout` - Maneja timeout
6. `test_youtube_video_dataclass` - Validación de tipos

**Output Structure** (YouTubeVideo):

```python
@dataclass
class YouTubeVideo:
    video_id: str
    title: str
    url: str
    duration_seconds: int
    view_count: int
    upload_date: str  # YYYYMMDD
    channel: str

    @property
    def duration_minutes(self) -> float:
        return self.duration_seconds / 60

    @property
    def quality_score(self) -> float:
        """Calculate weighted quality score"""
        # Views (normalized, peso 40%)
        # Duration proximity to 15 min (peso 20%)
        # Recency (peso 20%)
        # Completeness (peso 20%)
        ...
```

---

### Phase 3: Batch Processor (4 hours) ⏳

**Responsible**: Executor
**Dependencies**: Phase 2

**Subtasks**:

- [ ] Crear `youtube_script_generator/batch_processor.py`
- [ ] Función `download_audio_batch(videos: List[YouTubeVideo])`
- [ ] Función `transcribe_batch(audio_files: List[Path])`
- [ ] Reutilizar `yt_transcriber/downloader.py` para download
- [ ] Reutilizar `yt_transcriber/transcriber.py` para transcripción
- [ ] Progress bar con `rich` para batch operations
- [ ] Cleanup automático de archivos temporales
- [ ] Manejo de errores por video (continuar si uno falla)

**Success Criteria**:

- Descarga 15 audios en ~2-3 minutos
- Transcribe 15 videos en ~5-7 minutos (CUDA)
- Progress visible en terminal
- Maneja fallos individuales sin abortar batch
- Limpia archivos temporales al finalizar

**Tests Required** (5 tests):

1. `test_download_audio_batch_success` - Descarga múltiples videos
2. `test_transcribe_batch_success` - Transcribe múltiples audios
3. `test_batch_partial_failure` - Continúa si un video falla
4. `test_batch_cleanup` - Limpia temporales
5. `test_batch_progress_tracking` - Progress bar funciona

**Data Structure**:

```python
@dataclass
class VideoTranscript:
    video: YouTubeVideo
    transcript_text: str
    word_timestamps: List[dict]  # From Whisper
    language: str
    transcription_time_seconds: float
```

---

### Phase 4: Pattern Analyzer (4 hours) ⏳

**Responsible**: Executor
**Dependencies**: Phase 3

**Subtasks**:

- [ ] Crear `youtube_script_generator/pattern_analyzer.py`
- [ ] Función `analyze_video_patterns(transcript: VideoTranscript, video: YouTubeVideo)`
- [ ] Prompt estructurado para análisis con Gemini Pro
- [ ] Extracción de:
  - Estructura (hook, intro, desarrollo, conclusión con timestamps)
  - Hooks efectivos (primeros 30 seg)
  - CTAs (posición y texto exacto)
  - Vocabulario clave (términos técnicos, frases comunes)
  - Técnicas destacables
  - SEO (título, descripción si disponible)
- [ ] Dataclass `VideoAnalysis` con todos los campos
- [ ] Cálculo de effectiveness score usando metadata

**Success Criteria**:

- Analiza cada video en <5 segundos
- Extrae todos los patrones requeridos
- Effectiveness score refleja calidad del video
- Output estructurado y parseado correctamente

**Tests Required** (7 tests):

1. `test_analyze_video_patterns_success` - Análisis completo
2. `test_analyze_hook_extraction` - Extrae hook correctamente
3. `test_analyze_cta_extraction` - Extrae CTAs con posición
4. `test_analyze_structure_detection` - Detecta secciones
5. `test_analyze_vocabulary_extraction` - Extrae términos clave
6. `test_effectiveness_score_calculation` - Score basado en metadata
7. `test_video_analysis_dataclass` - Validación de tipos

**Analysis Prompt Template**:

```python
PATTERN_ANALYSIS_PROMPT = """
Analiza esta transcripción de video de YouTube y extrae patrones estructurales.

VIDEO INFO:
- Título: {video.title}
- Duración: {video.duration_minutes:.1f} minutos
- Views: {video.view_count:,}
- Canal: {video.channel}

TRANSCRIPCIÓN:
{transcript_text}

Extrae la siguiente información en formato JSON:

1. ESTRUCTURA:
   - hook_start: 0 (timestamp inicio hook en segundos)
   - hook_end: X (timestamp fin hook)
   - hook_text: "texto exacto del hook"
   - intro_end: X (timestamp fin introducción)
   - sections: [
       {{"title": "nombre sección", "start": X, "end": Y, "duration_min": Z}}
     ]
   - conclusion_start: X

2. HOOKS EFECTIVOS:
   - hook_type: "question" | "statistic" | "promise" | "problem"
   - hook_effectiveness: "high" | "medium" | "low"
   - hook_reason: "por qué es efectivo"

3. CTAS:
   - ctas: [
       {{
         "text": "texto exacto del CTA",
         "timestamp": X,
         "position_percent": Y,
         "type": "like" | "subscribe" | "comment" | "share"
       }}
     ]

4. VOCABULARIO CLAVE:
   - technical_terms: ["término1", "término2", ...]
   - common_phrases: ["frase1", "frase2", ...]
   - transition_phrases: ["ahora vamos a", "el siguiente paso", ...]

5. TÉCNICAS DESTACABLES:
   - techniques: [
       {{"name": "nombre técnica", "description": "cómo se usa"}}
     ]

6. SEO PATTERNS:
   - title_keywords: ["keyword1", "keyword2", ...]
   - estimated_tags: ["tag1", "tag2", ...]

Responde SOLO con el JSON, sin explicación adicional.
"""
```

**Output Structure** (VideoAnalysis):

```python
@dataclass
class VideoAnalysis:
    video: YouTubeVideo

    # Estructura
    hook_start: int  # segundos
    hook_end: int
    hook_text: str
    hook_type: str
    hook_effectiveness: str
    intro_end: int
    sections: List[dict]
    conclusion_start: int

    # CTAs
    ctas: List[dict]  # [{text, timestamp, position_percent, type}]

    # Vocabulario
    technical_terms: List[str]
    common_phrases: List[str]
    transition_phrases: List[str]

    # Técnicas
    techniques: List[dict]  # [{name, description}]

    # SEO
    title_keywords: List[str]
    estimated_tags: List[str]

    # Calidad
    effectiveness_score: float  # 1-5 basado en metadata

    # Raw
    raw_analysis: str  # JSON completo de Gemini
```

---

### Phase 5: Synthesis Engine (4 hours) ⏳

**Responsible**: Executor
**Dependencies**: Phase 4

**Subtasks**:

- [ ] Crear `youtube_script_generator/synthesizer.py`
- [ ] Función `synthesize_patterns(analyses: List[VideoAnalysis]) -> PatternSynthesis`
- [ ] Prompt estructurado para síntesis con Gemini Pro
- [ ] Ponderación por effectiveness_score
- [ ] Categorización de información:
  - Top 10 hooks (ordenados por effectiveness)
  - Estructura óptima (promedio ponderado)
  - CTAs más efectivos (frecuencia + posición)
  - Vocabulario común (frecuencia)
  - Técnicas únicas destacables
  - SEO patterns
- [ ] Generación de Markdown synthesis report
- [ ] Preservación de información crítica

**Success Criteria**:

- Síntesis completa en <30 segundos
- Preserva top patterns de cada categoría
- Pondera correctamente por quality score
- Markdown report legible y bien estructurado
- No pierde información crítica

**Tests Required** (6 tests):

1. `test_synthesize_patterns_success` - Síntesis completa
2. `test_synthesize_weighting` - Pondera por effectiveness
3. `test_synthesize_top_hooks` - Extrae top 10 hooks
4. `test_synthesize_structure_average` - Calcula promedios
5. `test_synthesize_markdown_generation` - Genera Markdown
6. `test_pattern_synthesis_dataclass` - Validación de tipos

**Synthesis Prompt Template**:

```python
SYNTHESIS_PROMPT = """
Tienes {num_videos} análisis de videos exitosos de YouTube sobre "{topic}".

Tu tarea es crear un INFORME SINTETIZADO con las mejores prácticas.

IMPORTANTE: Pondera la información por el effectiveness_score de cada video.
Videos con score alto (4-5) tienen más peso que videos con score bajo (1-2).

ANÁLISIS INDIVIDUALES:
{analyses_json}

Genera un informe estructurado con:

1. HOOKS MÁS EFECTIVOS (Top 10):
   - Lista los 10 hooks más impactantes
   - Clasifica por tipo: question, statistic, promise, problem
   - Indica frecuencia de uso y effectiveness promedio
   - Proporciona texto exacto como ejemplo

2. ESTRUCTURA ÓPTIMA:
   - Duración promedio de hook: X-Y segundos (weighted average)
   - Duración promedio de intro: X-Y segundos
   - Número de secciones: X (moda)
   - Duración de cada sección: X-Y minutos (promedio)
   - Total duration target: X minutos

3. CTAs EFECTIVOS:
   - Posiciones más comunes: X%, Y%, Z% del video
   - Tipos de CTAs ordenados por frecuencia
   - Frases exactas más usadas (top 5)
   - Mejores momentos para insertar CTA

4. VOCABULARIO CLAVE:
   - Términos técnicos más frecuentes (top 20)
   - Frases de transición comunes (top 10)
   - Palabras que indican engagement alto

5. TÉCNICAS DESTACABLES:
   - Patrones únicos de videos top (score >4)
   - Técnicas que se repiten en múltiples videos
   - Innovaciones destacables

6. SEO PATTERNS:
   - Palabras clave más comunes en títulos
   - Estructura de títulos efectivos
   - Tags más relevantes

Formato de output: JSON estructurado.
"""
```

**Output Structure** (PatternSynthesis):

```python
@dataclass
class PatternSynthesis:
    topic: str
    num_videos_analyzed: int

    # Top patterns
    top_hooks: List[dict]  # [{text, type, effectiveness, frequency}]
    optimal_structure: dict  # {hook_duration, intro_duration, sections, ...}
    effective_ctas: List[dict]  # [{text, position, frequency}]
    key_vocabulary: dict  # {technical_terms, transitions, ...}
    notable_techniques: List[dict]  # [{name, description, frequency}]
    seo_patterns: dict  # {title_keywords, tags, ...}

    # Metadata
    average_effectiveness: float
    synthesis_timestamp: datetime

    # Report
    markdown_report: str  # Full synthesis report
```

---

### Phase 6: Script Generator (3 hours) ⏳

**Responsible**: Executor
**Dependencies**: Phase 5

**Subtasks**:

- [ ] Crear `youtube_script_generator/script_generator.py`
- [ ] Función `generate_script(user_idea: str, synthesis: PatternSynthesis) -> GeneratedScript`
- [ ] Prompt enriquecido con síntesis completa
- [ ] Generación con Gemini Pro
- [ ] Incluir SEO optimization (título, descripción, tags)
- [ ] Output en Markdown estructurado
- [ ] Timestamps estimados en guión

**Success Criteria**:

- Genera guión en <20 segundos
- Aplica patrones de synthesis
- Calidad esperada 90-95/100
- Incluye SEO completo
- Markdown bien formateado

**Tests Required** (5 tests):

1. `test_generate_script_success` - Generación completa
2. `test_generate_script_uses_synthesis` - Aplica patrones
3. `test_generate_script_seo` - Incluye título/descripción/tags
4. `test_generate_script_structure` - Tiene todas las secciones
5. `test_generated_script_dataclass` - Validación de tipos

**Generation Prompt Template**:

```python
SCRIPT_GENERATION_PROMPT = """
Eres un guionista experto de YouTube. Vas a crear un guion profesional sobre:
"{user_idea}"

CONTEXTO: Has analizado {num_videos} videos exitosos sobre este tema.
Aplica las mejores prácticas identificadas a continuación.

MEJORES PRÁCTICAS IDENTIFICADAS:
{synthesis_markdown}

INSTRUCCIONES:
1. Usa uno de los top hooks identificados (adapta al tema)
2. Sigue la estructura óptima identificada
3. Inserta CTAs en las posiciones recomendadas
4. Usa el vocabulario clave del nicho
5. Aplica las técnicas destacables donde sea apropiado

REQUISITOS:
- Duración objetivo: {target_duration} minutos
- Incluir timestamps [MM:SS]
- 2-3 CTAs en posiciones óptimas
- Vocabulario técnico apropiado
- Tono profesional pero accesible

ESTRUCTURA OBLIGATORIA:
{structure_template}

SEO OPTIMIZATION:
- Título: 50-70 caracteres, keywords al inicio
- Descripción: 150-200 palabras, incluir keywords
- Tags: 15-20 tags relevantes basados en análisis

Genera el guion completo en formato Markdown.
"""
```

**Output Structure** (GeneratedScript):

```python
@dataclass
class GeneratedScript:
    user_idea: str

    # Guión
    script_markdown: str  # Guión completo con timestamps
    estimated_duration_minutes: int
    word_count: int

    # SEO
    seo_title: str
    seo_description: str
    seo_tags: List[str]

    # Metadata
    synthesis_used: str  # Topic de synthesis
    num_reference_videos: int
    generation_timestamp: datetime
    cost_usd: float

    # Quality
    estimated_quality_score: int  # 1-100
```

---

### Phase 7: CLI Integration (2 hours) ⏳

**Responsible**: Executor
**Dependencies**: Phase 6

**Subtasks**:

- [ ] Extender `yt_transcriber/cli.py` con comando `generate-from-search`
- [ ] Argumentos: `--idea`, `--max-videos`, `--output`, `--no-optimize`
- [ ] Progress tracking con `rich`
- [ ] Mostrar estadísticas al finalizar
- [ ] Guardar synthesis como referencia
- [ ] Error handling y mensajes claros

**Success Criteria**:

- CLI intuitiva y fácil de usar
- Progress visible para cada fase
- Estadísticas útiles (tiempo, coste, calidad)
- Guarda synthesis y script
- Manejo de errores claro

**Tests Required** (4 tests):

1. `test_cli_generate_help` - Muestra ayuda
2. `test_cli_generate_missing_idea` - Error sin idea
3. `test_cli_generate_success` - E2E flow completo
4. `test_cli_generate_progress` - Progress bars funcionan

**CLI Usage Example**:

```bash
uv run python -m yt_transcriber.cli generate-from-search \
  --idea "crear proyecto con FastAPI en Python" \
  --max-videos 15 \
  --output "scripts/fastapi_proyecto.md"
```

**Expected Terminal Output**:

```
🎬 YouTube-Powered Script Generator
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 Idea: "crear proyecto con FastAPI en Python"

🔧 Optimizando query de búsqueda...
   ✓ Query optimizada: "FastAPI Python proyecto tutorial REST API"

🔍 Buscando videos en YouTube...
   [████████████████████] 15/15 videos encontrados (12s)
   └─ Duración promedio: 14.3 min, Views promedio: 45.2K

📥 Descargando audios...
   [████████████████████] 15/15 descargados (2m 18s)

🎤 Transcribiendo videos (CUDA)...
   [████████████████████] 15/15 transcritos (5m 42s)
   └─ RTX 3060: 23 seg/video promedio

📊 Analizando patrones...
   [████████████████████] 15/15 análisis (1m 35s)
   └─ Coste: 0.120€

🧠 Sintetizando mejores prácticas...
   ✓ Síntesis completada (24s)
   └─ Top 10 hooks, estructura óptima, 8 técnicas identificadas
   └─ Coste: 0.020€

✍️ Generando guión optimizado...
   ✓ Guión generado (18s)
   └─ Coste: 0.018€

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Proceso completado en 10m 31s
💰 Coste total: 0.158€

📄 Archivos generados:
   ├─ scripts/fastapi_proyecto.md (guión final)
   └─ analysis/fastapi_proyecto_synthesis.md (referencia)

📊 Estadísticas del guión:
   - Título: "FastAPI REST API Completa - De Cero a Producción"
   - Duración estimada: 14 minutos
   - Palabras: 1,247
   - Secciones: 7
   - CTAs: 3
   - Tags SEO: 18
   - Calidad estimada: 92/100

🎯 Basado en análisis de 15 videos (avg. effectiveness: 4.2/5)
```

---

### Phase 8: Testing & Documentation (3 hours) ⏳

**Responsible**: Executor
**Dependencies**: Phase 7

**Subtasks**:

- [ ] Tests unitarios para cada módulo (ya definidos en fases)
- [ ] Test de integración E2E completo
- [ ] Validar con idea real y verificar output
- [ ] Actualizar README con nuevo comando
- [ ] Crear `docs/YOUTUBE_SCRIPT_GENERATOR.md` con guía detallada
- [ ] Actualizar AGENTS.md con nueva arquitectura
- [ ] Coverage report (objetivo >70%)

**Success Criteria**:

- Todos los tests pasan
- Coverage >70%
- README actualizado con ejemplos
- Documentación completa
- Guía de troubleshooting

**Tests Required**:

- Unit tests: ~35 tests (ya definidos en fases anteriores)
- Integration tests: 3 tests
  - `test_e2e_full_workflow` - Workflow completo con idea real
  - `test_e2e_cost_validation` - Coste dentro de límites
  - `test_e2e_output_quality` - Verifica calidad de output

---

## Project Status Board

### ✅ Completed Tasks

- [x] Análisis de opciones: RAG vs Síntesis Contextual
- [x] Decisión: yt-dlp vs YouTube API
- [x] Análisis de costes y tiempos
- [x] Plan de implementación detallado (8 fases)

### 🔄 In Progress

- [ ] Ninguna (esperando aprobación para empezar)

### 📋 To Do (Prioridad)

1. **HIGH**: Phase 0 - Setup & Configuration
2. **HIGH**: Phase 1 - Query Optimizer
3. **HIGH**: Phase 2 - YouTube Searcher
4. **HIGH**: Phase 3 - Batch Processor
5. **MEDIUM**: Phase 4 - Pattern Analyzer
6. **MEDIUM**: Phase 5 - Synthesis Engine
7. **LOW**: Phase 6 - Script Generator
8. **LOW**: Phase 7 - CLI Integration
9. **LOW**: Phase 8 - Testing & Documentation

### ⏸️ Blocked

- Ninguna

---

## Executor's Feedback or Assistance Requests

### Questions for Planner

_Ninguna aún - fase de planificación completada._

### Blockers Encountered

_Ninguno aún._

### Lessons Learned During Execution

_Se actualizará durante la implementación._

---

## Technical Specifications

### Dependencies to Add

```toml
[project.dependencies]
google-generativeai = "^0.3.0"  # Gemini API
rich = "^13.7.0"  # CLI progress bars y formatting
```

### Environment Variables

```bash
# .env
GOOGLE_API_KEY=your_api_key_here
GEMINI_PRO_MODEL=gemini-2.5-pro
```

### File Structure

```
yt-video-summarizer/
├── yt_transcriber/          # EXISTENTE - MANTENER Y EXTENDER
│   ├── cli.py              # EXTENDER con generate-from-search
│   ├── downloader.py       # REUTILIZAR
│   ├── transcriber.py      # REUTILIZAR
│   └── config.py           # EXTENDER con Gemini config
│
├── youtube_script_generator/  # NUEVO
│   ├── __init__.py
│   ├── query_optimizer.py     # Phase 1: Optimiza search query
│   ├── youtube_searcher.py    # Phase 2: Busca videos con yt-dlp
│   ├── batch_processor.py     # Phase 3: Download + transcribe batch
│   ├── pattern_analyzer.py    # Phase 4: Analiza cada video
│   ├── synthesizer.py         # Phase 5: Sintetiza N análisis
│   ├── script_generator.py    # Phase 6: Genera guión final
│   └── models.py              # Dataclasses compartidas
│
├── output_scripts/         # Guiones generados
├── output_analysis/        # Síntesis de referencia
└── temp_batch/            # Temporales (auto-limpieza)
    ├── audios/
    └── transcripts/

test/
└── test_youtube_script_generator/
    ├── test_query_optimizer.py
    ├── test_youtube_searcher.py
    ├── test_batch_processor.py
    ├── test_pattern_analyzer.py
    ├── test_synthesizer.py
    ├── test_script_generator.py
    ├── test_cli_integration.py
    └── test_e2e_integration.py
```

### Cost Breakdown (15-minute videos, 15 videos analyzed)

| Component                        | Tokens/Calls              | Cost per Unit  | Total       |
| -------------------------------- | ------------------------- | -------------- | ----------- |
| **Query Optimization**           | 200 in + 50 out           | $1.25/M + $5/M | ~$0.0005    |
| **YouTube Search (yt-dlp)**      | -                         | Gratis         | $0          |
| **Download 15 audios**           | -                         | Gratis         | $0          |
| **Transcription (Whisper CUDA)** | -                         | Gratis (local) | $0          |
| **Pattern Analysis (15 videos)** | 15 × (4.2K in + 1.5K out) | $1.25/M + $5/M | ~$0.120     |
| **Synthesis**                    | 25K in + 3K out           | $1.25/M + $5/M | ~$0.046     |
| **Script Generation**            | 6K in + 3K out            | $1.25/M + $5/M | ~$0.023     |
| **TOTAL**                        |                           |                | **~$0.190** |

**Notas:**

- Síntesis usa mucho input (15 análisis completos)
- Coste podría reducirse si resumimos análisis antes de synthesis
- Con tier gratuito Gemini: primeros ~50 guiones gratis/día

### Time Breakdown (Sequential execution)

| Phase                | Time          | Notas                   |
| -------------------- | ------------- | ----------------------- |
| Query optimization   | 2-3 seg       | Gemini API call         |
| YouTube search       | 10-15 seg     | yt-dlp búsqueda         |
| Download 15 audios   | 2-3 min       | Depende de conexión     |
| Transcription (CUDA) | 5-7 min       | RTX 3060: ~23 seg/video |
| Pattern analysis     | 1.5-2 min     | 15 × ~6 seg (Gemini)    |
| Synthesis            | 20-30 seg     | Gemini con input largo  |
| Script generation    | 15-20 seg     | Gemini                  |
| **TOTAL**            | **10-14 min** | Tiempo real de usuario  |

**Optimizaciones posibles Phase 2**:

- Transcripción paralela: 5-7 min → 2-3 min (asyncio)
- Análisis paralelo: 1.5-2 min → 30-40 seg (batch API)

---

## Risk Assessment

### High Risk

**Yt-dlp bloqueado por YouTube**

- **Probabilidad**: Baja (yt-dlp muy mantenido)
- **Impacto**: Alto (feature no funciona)
- **Mitigation**: Implementar fallback a YouTube Data API
- **Señales de alerta**: Errores HTTP 429, 403 repetidos

### Medium Risk

**Gemini API rate limits**

- **Probabilidad**: Media (tier gratuito limitado)
- **Impacto**: Medio (proceso más lento)
- **Mitigation**: Implementar retry logic con exponential backoff
- **Límites conocidos**: 60 requests/min en tier gratuito

**Transcripción lenta sin CUDA**

- **Probabilidad**: Baja (usuario tiene RTX 3060)
- **Impacto**: Alto (10-14 min → 40-60 min)
- **Mitigation**: Detectar CUDA, avisar si no disponible, sugerir menos videos

### Low Risk

**Síntesis pierde información crítica**

- **Probabilidad**: Baja (prompt estructurado)
- **Impacto**: Medio (calidad reducida)
- **Mitigation**: Validar synthesis manualmente en testing, ajustar prompt

**Videos sin transcripción disponible**

- **Probabilidad**: Baja (la mayoría tienen audio)
- **Impacto**: Bajo (se omite ese video)
- **Mitigation**: Manejar error, continuar con otros videos

---

## Quality Metrics

### Code Quality Targets

- **Test Coverage**: >70%
- **Type Hints**: 100% en funciones públicas
- **Docstrings**: 100% en módulos/funciones públicas
- **Linting**: 0 errores Ruff
- **Type Checking**: 0 errores Mypy

### Output Quality Targets

- **Script Quality**: 90-95/100 (evaluación manual)
- **Synthesis Completeness**: Preserva top 10 de cada categoría
- **SEO Optimization**: Título/descripción/tags presentes
- **Structure Adherence**: Sigue estructura óptima identificada

### Performance Targets

- **Total Time**: <15 minutos por guión
- **Cost**: <$0.20 por guión
- **Success Rate**: >95% (manejo robusto de errores)

---

## Next Steps

1. **Planner aprueba este plan** → Executor comienza Phase 0
2. **Usuario confirma presupuesto** (~$0.19/guión aceptable)
3. **Usuario provee GOOGLE_API_KEY** o crea cuenta
4. **Executor implementa Phase 0** y reporta progreso

**IMPORTANTE**: Después de Phase 3 (Batch Processor), hacer **CHECKPOINT**:

- Ejecutar con 3 videos de prueba
- Verificar transcripciones correctas
- Validar tiempos y costes reales
- Si OK → Continuar Phase 4-8
- Si NOK → Ajustar y re-evaluar

---

**Última actualización**: 2025-01-03 (Planning Phase)
**Próxima revisión**: Después de Phase 0 completada
**Aprobación pendiente**: Usuario confirma stack técnico y costes
