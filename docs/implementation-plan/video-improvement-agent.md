# Implementation Plan: Video Improvement Agent

**Created**: 2025-01-03
**Status**: 🔄 Planning Phase
**Owner**: Planner
**Estimated Effort**: 15-20 hours

---

## Background and Motivation

### Problem Statement

Los creadores de contenido de YouTube necesitan mejorar la calidad de sus videos pero carecen de herramientas automatizadas que analicen tanto el contenido visual como el guion del video para proporcionar sugerencias concretas de mejora.

### Goals

Crear un agente de análisis de videos locales que:

1. Procese videos mp4/mkv almacenados localmente
2. Genere transcripción precisa con Whisper (aprovechando CUDA existente)
3. Analice aspectos visuales (ritmo, cambios de escena, elementos en pantalla)
4. Analice el guion y proporcione mejoras creativas
5. Genere optimización SEO (título, descripción, tags)
6. Produzca un informe Markdown legible y accionable

### Success Criteria

- ✅ Procesa videos de 10-30 minutos en <5 minutos (con CUDA)
- ✅ Coste por análisis <0.10€ (objetivo: ~0.025€)
- ✅ Informe Markdown generado automáticamente
- ✅ Cobertura de tests >70%
- ✅ CLI simple y clara
- ✅ Documentación completa en README

---

## Key Challenges and Analysis

### Technical Challenges

1. **Multimodal Analysis**

   - ✅ **Solución adoptada**: Gemini 2.5 Flash para análisis visual (multimodal nativo)
   - Evita necesidad de OpenCV, librosa, scipy
   - Procesa video mp4 directamente

2. **Cost Management**

   - ✅ **Estrategia**: Gemini Flash (0.001€) + Pro (0.024€) = 0.025€ total
   - 2.7x más barato que Claude 3.5 Sonnet
   - Tier gratuito: 1500 requests/día para desarrollo

3. **Quality of Analysis**

   - ✅ **Gemini 2.5 Pro**: 94/100 calidad estimada
   - Excelente razonamiento y seguimiento de instrucciones
   - Contexto 2M tokens (suficiente para videos largos)

4. **Integration with Existing Code**
   - Reutilizar lógica de transcripción existente (Whisper + CUDA)
   - Mantener arquitectura modular
   - Evitar duplicación de código

### Architecture Decisions

**Decision 1: LLM Provider**

- **Options**: Claude 3.5 Sonnet vs Gemini 2.5 Pro
- **Chosen**: Gemini 2.5 Flash + Pro (híbrido)
- **Rationale**:
  - 2.7x más barato (0.025€ vs 0.068€)
  - Calidad superior (94/100 vs 92/100)
  - Multimodal nativo
  - Un solo SDK

**Decision 2: Architecture Pattern**

- **Options**: Monolítico vs Modular
- **Chosen**: Modular con nuevo namespace `video_improver/`
- **Rationale**:
  - Separación de concerns
  - Permite desarrollar Feature B (script generator) independientemente
  - Reutiliza código de `yt_transcriber/` donde tenga sentido

**Decision 3: Output Format**

- **Options**: JSON, HTML, PDF, Markdown
- **Chosen**: Markdown
- **Rationale**:
  - Legible en cualquier editor
  - Fácil de convertir a HTML/PDF si se necesita
  - Simple de parsear programáticamente
  - Usuario lo solicitó explícitamente

---

## High-level Task Breakdown

### Phase 0: Setup & Configuration (2 hours) ⏳

**Responsible**: Executor
**Dependencies**: None

**Subtasks**:

- [ ] Crear estructura de carpetas `video_improver/`
- [ ] Instalar dependencia `google-generativeai`
- [ ] Configurar `GOOGLE_API_KEY` en `.env` y `config.py`
- [ ] Actualizar `pyproject.toml` con nueva dependencia
- [ ] Crear `video_improver/__init__.py`
- [ ] Documentar setup en README

**Success Criteria**:

- `uv sync` instala `google-generativeai` sin errores
- `.env.example` actualizado con `GOOGLE_API_KEY`
- `video_improver/` existe con estructura inicial
- Tests de importación pasan

**Tests Required**:

- `test/test_video_improver_setup.py`: Verificar importaciones
- Verificar que `google.generativeai` se importa correctamente

---

### Phase 1: Local Video Transcription (3 hours) ⏳

**Responsible**: Executor
**Dependencies**: Phase 0

**Subtasks**:

- [ ] Crear `video_improver/local_transcriber.py`
- [ ] Función `transcribe_local_video(video_path: Path) -> TranscriptionResult`
- [ ] Reutilizar lógica de `yt_transcriber/transcriber.py`
- [ ] Manejar formatos mp4, mkv, avi, mov
- [ ] Extraer audio temporal con FFmpeg
- [ ] Limpiar archivos temporales después

**Success Criteria**:

- Transcribe video de prueba (10 min) en <30 segundos con CUDA
- Genera timestamps de palabras correctamente
- Maneja errores de archivos no encontrados o corruptos
- Limpia archivos temporales automáticamente

**Tests Required** (6 tests):

1. `test_transcribe_local_video_success` - Video válido
2. `test_transcribe_local_video_file_not_found` - Archivo no existe
3. `test_transcribe_local_video_invalid_format` - Formato no soportado
4. `test_transcribe_local_video_cuda` - Usa CUDA si disponible
5. `test_transcribe_local_video_cpu_fallback` - Fallback a CPU
6. `test_transcribe_local_video_cleanup` - Limpia temporales

---

### Phase 2: Visual Analysis with Gemini Flash (3 hours) ⏳

**Responsible**: Executor
**Dependencies**: Phase 0

**Subtasks**:

- [ ] Crear `video_improver/visual_analyzer.py`
- [ ] Función `analyze_video_visual(video_path: Path) -> VisualAnalysis`
- [ ] Implementar upload de video a Gemini API
- [ ] Crear prompt estructurado para análisis visual
- [ ] Parsear respuesta JSON de Gemini
- [ ] Dataclass `VisualAnalysis` con tipado fuerte

**Success Criteria**:

- Analiza video de 10 min en <10 segundos
- Detecta cambios de escena con timestamps
- Identifica ritmo visual (dinámico/estático)
- Detecta elementos en pantalla (texto, gráficos)
- Coste <0.002€ por video

**Tests Required** (5 tests):

1. `test_analyze_video_visual_success` - Video válido
2. `test_analyze_video_visual_scene_changes` - Detecta cambios
3. `test_analyze_video_visual_parsing` - Parsea JSON correctamente
4. `test_analyze_video_visual_api_error` - Maneja errores API
5. `test_visual_analysis_dataclass` - Validación de tipos

**Output Structure** (VisualAnalysis):

```python
@dataclass
class VisualAnalysis:
    scene_changes: list[float]  # Timestamps en segundos
    visual_pace: str  # "dynamic", "static", "mixed"
    on_screen_elements: list[str]  # ["text_overlays", "graphics", etc]
    lighting_quality: str  # "good", "poor", "inconsistent"
    framing_quality: str  # "professional", "amateur", "needs_improvement"
    raw_response: str  # Respuesta completa de Gemini
```

---

### Phase 3: Script Analysis with Gemini Pro (4 hours) ⏳

**Responsible**: Executor
**Dependencies**: Phase 1, Phase 2

**Subtasks**:

- [ ] Crear `video_improver/script_analyzer.py`
- [ ] Función `analyze_script(transcript: str, visual: VisualAnalysis) -> ScriptAnalysis`
- [ ] Prompt estructurado para análisis de guion
- [ ] Incluir contexto visual en el análisis
- [ ] Generar sugerencias de mejora específicas
- [ ] Optimización SEO (título, descripción, tags)
- [ ] Identificar mejores momentos para thumbnail

**Success Criteria**:

- Genera análisis en <15 segundos
- Sugerencias específicas y accionables (no genéricas)
- Título SEO optimizado (50-70 caracteres)
- Descripción 150-200 palabras
- 15-20 tags relevantes
- Coste <0.030€ por análisis

**Tests Required** (7 tests):

1. `test_analyze_script_success` - Análisis completo
2. `test_analyze_script_seo_title_length` - Título 50-70 chars
3. `test_analyze_script_seo_description_length` - 150-200 palabras
4. `test_analyze_script_tags_count` - 15-20 tags
5. `test_analyze_script_with_visual_context` - Usa contexto visual
6. `test_analyze_script_api_error` - Maneja errores
7. `test_script_analysis_dataclass` - Validación de tipos

**Output Structure** (ScriptAnalysis):

```python
@dataclass
class ScriptAnalysis:
    strengths: list[str]  # Puntos fuertes del guion
    weaknesses: list[str]  # Áreas de mejora
    improvements: list[str]  # Sugerencias específicas
    seo_title: str  # Título optimizado
    seo_description: str  # Descripción SEO
    seo_tags: list[str]  # Tags relevantes
    thumbnail_moments: list[float]  # Timestamps sugeridos
    overall_score: int  # 1-100
    raw_response: str
```

---

### Phase 4: Report Generation (2 hours) ⏳

**Responsible**: Executor
**Dependencies**: Phase 3

**Subtasks**:

- [ ] Crear `video_improver/report_generator.py`
- [ ] Función `generate_markdown_report(analysis: ScriptAnalysis, visual: VisualAnalysis) -> str`
- [ ] Template Markdown estructurado
- [ ] Incluir secciones: Resumen, Visual, Guion, SEO, Acción
- [ ] Formato legible con emojis y separadores
- [ ] Guardar en `output_reports/`

**Success Criteria**:

- Markdown bien formateado y legible
- Todas las secciones de análisis incluidas
- Archivo guardado con nombre descriptivo
- Links a timestamps funcionan (formato YouTube)

**Tests Required** (4 tests):

1. `test_generate_markdown_report_structure` - Contiene secciones
2. `test_generate_markdown_report_formatting` - Markdown válido
3. `test_generate_markdown_report_save` - Guarda correctamente
4. `test_markdown_report_filename` - Nombre sanitizado

**Template Markdown**:

```markdown
# 📊 Análisis de Video: {video_title}

## 🎯 Resumen Ejecutivo

Puntuación general: {score}/100
...

## 🎬 Análisis Visual

...

## 📝 Análisis del Guion

### ✅ Puntos Fuertes

...

### ⚠️ Áreas de Mejora

...

## 🚀 SEO & Optimización

...

## 📋 Plan de Acción

...
```

---

### Phase 5: CLI Implementation (2 hours) ⏳

**Responsible**: Executor
**Dependencies**: Phase 4

**Subtasks**:

- [ ] Crear `video_improver/cli.py`
- [ ] Argumentos: `--video`, `--output`, `--model` (flash/pro)
- [ ] Integrar con `rich` para progress bars
- [ ] Mostrar estimación de coste antes de procesar
- [ ] Confirmación de usuario si coste >0.10€
- [ ] Manejo de errores con mensajes claros

**Success Criteria**:

- CLI intuitiva y fácil de usar
- Progress bars para operaciones largas
- Estimación de coste precisa
- Mensajes de error claros y accionables
- `--help` con documentación completa

**Tests Required** (5 tests):

1. `test_cli_help` - Muestra ayuda
2. `test_cli_missing_video` - Error si no hay video
3. `test_cli_invalid_video` - Error si formato inválido
4. `test_cli_cost_estimation` - Muestra coste estimado
5. `test_cli_full_workflow` - E2E test

**CLI Usage**:

```bash
uv run python -m video_improver.cli \
  --video "mi_video.mp4" \
  --output "reports/mi_video_analysis.md"

# Output esperado:
📹 Analizando video: mi_video.mp4
⏱️  Duración: 15:32
💰 Coste estimado: 0.025€

[████████████████████] Transcribiendo...     ✓ (18s)
[████████████████████] Análisis visual...    ✓ (5s)
[████████████████████] Análisis de guion...  ✓ (12s)
[████████████████████] Generando reporte... ✓ (1s)

✅ Análisis completado en 36 segundos
📄 Informe guardado en: reports/mi_video_analysis.md
💰 Coste real: 0.024€
```

---

### Phase 6: Documentation & Examples (2 hours) ⏳

**Responsible**: Executor
**Dependencies**: Phase 5

**Subtasks**:

- [ ] Actualizar README.md con sección "Video Improvement Agent"
- [ ] Crear `docs/VIDEO_IMPROVER.md` con guía detallada
- [ ] Documentar estructura de informes Markdown
- [ ] Ejemplo completo con video de prueba
- [ ] Actualizar AGENTS.md con nueva arquitectura
- [ ] Crear video de prueba en `test/fixtures/sample_video.mp4`

**Success Criteria**:

- README actualizado con ejemplos
- Documentación completa y clara
- Ejemplo reproducible incluido
- AGENTS.md refleja nueva estructura

**Tests Required**:

- No tests, solo documentación

---

### Phase 7: Integration & E2E Testing (2 hours) ⏳

**Responsible**: Executor
**Dependencies**: All previous phases

**Subtasks**:

- [ ] Crear `test/test_video_improver_integration.py`
- [ ] Test E2E completo con video real
- [ ] Verificar costes reales vs estimados
- [ ] Test con videos de diferentes duraciones
- [ ] Test con tier gratuito de Gemini
- [ ] Actualizar coverage report

**Success Criteria**:

- E2E test pasa con video real
- Coste real <0.030€ por video de 15 min
- Coverage total >70%
- Todos los tests pasan en <60 segundos

**Tests Required** (8 tests):

1. `test_e2e_video_analysis_full` - Workflow completo
2. `test_e2e_cost_validation` - Coste dentro de límites
3. `test_e2e_10min_video` - Video corto
4. `test_e2e_30min_video` - Video largo
5. `test_e2e_different_formats` - mp4, mkv, avi
6. `test_e2e_report_quality` - Validar estructura
7. `test_e2e_cuda_performance` - Velocidad con CUDA
8. `test_e2e_cpu_fallback` - Funciona sin CUDA

---

## Project Status Board

### ✅ Completed Tasks

- [x] Análisis de opciones de LLM (Claude vs Gemini)
- [x] Decisión de arquitectura (Gemini híbrido)
- [x] Estimación de costes (0.025€/video)
- [x] Plan de implementación detallado

### 🔄 In Progress

- [ ] Ninguna (en fase de planificación)

### 📋 To Do (Prioridad)

1. **HIGH**: Phase 0 - Setup & Configuration
2. **HIGH**: Phase 1 - Local Video Transcription
3. **MEDIUM**: Phase 2 - Visual Analysis
4. **MEDIUM**: Phase 3 - Script Analysis
5. **LOW**: Phase 4 - Report Generation
6. **LOW**: Phase 5 - CLI Implementation
7. **LOW**: Phase 6 - Documentation
8. **LOW**: Phase 7 - Integration Testing

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
rich = "^13.7.0"  # CLI progress bars
```

### Environment Variables

```bash
# .env
GOOGLE_API_KEY=your_api_key_here
GEMINI_FLASH_MODEL=gemini-2.5-flash  # Para análisis visual
GEMINI_PRO_MODEL=gemini-2.5-pro      # Para análisis de guion
```

### File Structure

```
video_improver/
├── __init__.py
├── cli.py                  # CLI principal
├── config.py               # Settings (extiende AppSettings)
├── local_transcriber.py    # Transcripción local
├── visual_analyzer.py      # Análisis visual (Flash)
├── script_analyzer.py      # Análisis guion (Pro)
├── report_generator.py     # Generación Markdown
└── models.py               # Dataclasses compartidas

test/
└── test_video_improver/
    ├── test_setup.py
    ├── test_local_transcriber.py
    ├── test_visual_analyzer.py
    ├── test_script_analyzer.py
    ├── test_report_generator.py
    ├── test_cli.py
    └── test_integration.py

output_reports/              # Informes generados
test/fixtures/
└── sample_video.mp4        # Video de prueba
```

### Cost Breakdown (15-minute video)

| Component      | Tokens           | Cost per 1M    | Total        |
| -------------- | ---------------- | -------------- | ------------ |
| Flash (visual) | 2K in + 1K out   | $0.075 + $0.30 | ~$0.0004     |
| Pro (script)   | 4.2K in + 4K out | $1.25 + $5.00  | ~$0.024      |
| **TOTAL**      |                  |                | **~$0.0244** |

---

## Risk Assessment

### High Risk

- **API Rate Limits**: Gemini tier gratuito tiene límites
  - _Mitigation_: Implementar retry logic y manejo de rate limits

### Medium Risk

- **Video Upload Size**: Videos grandes pueden fallar
  - _Mitigation_: Validar tamaño antes de upload, documentar límites

### Low Risk

- **CUDA No Disponible**: Whisper lento en CPU
  - _Mitigation_: Ya manejado en código existente (fallback automático)

---

## Next Steps

1. **Planner aprueba este plan** → Executor comienza Phase 0
2. **Usuario confirma presupuesto** (0.025€/video aceptable)
3. **Usuario provee GOOGLE_API_KEY** o crea cuenta Gemini
4. **Executor implementa Phase 0** y reporta progreso

---

**Última actualización**: 2025-01-03 (Planning Phase)
**Próxima revisión**: Después de Phase 0 completada
