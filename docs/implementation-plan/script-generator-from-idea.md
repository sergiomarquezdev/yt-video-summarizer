# Implementation Plan: Script Generator from Idea

**Created**: 2025-01-03
**Status**: 📋 Planned (Not Started)
**Owner**: Planner
**Estimated Effort**: 8-10 hours

---

## Background and Motivation

### Problem Statement
Los creadores de contenido a menudo tienen ideas para videos pero les falta estructura o no saben cómo convertir una idea simple en un guion completo optimizado para YouTube. El proceso manual de crear guiones consume tiempo y requiere experiencia en escritura y SEO.

### Goals
Crear un endpoint/comando independiente que:
1. Reciba una idea textual simple (ej: "Video sobre cómo crear una aplicación Python con FastAPI con las mejores prácticas")
2. Genere un guion completo de YouTube con estructura profesional
3. Incluya optimización SEO (título, descripción, tags)
4. Proporcione sugerencias de thumbnail y CTA (call-to-action)
5. Sea completamente independiente del análisis de videos (desarrollo aislado)

### Success Criteria
- ✅ Genera guion de 10-15 minutos en <30 segundos
- ✅ Coste por generación <0.05€
- ✅ Guion estructurado con intro, cuerpo, conclusión
- ✅ SEO optimizado automáticamente
- ✅ Output en Markdown legible
- ✅ Cobertura de tests >70%

---

## Key Challenges and Analysis

### Technical Challenges

1. **Prompt Engineering**
   - Diseñar prompt que genere guiones consistentes y de calidad
   - Evitar respuestas genéricas o poco accionables
   - Mantener tono y estilo apropiado para YouTube

2. **Diferenciación de Prompts**
   - **Script Generator**: Crear guion desde cero (creativo)
   - **Video Analyzer**: Analizar guion existente (analítico)
   - Prompts completamente diferentes, NO reutilizables

3. **Structure Consistency**
   - Asegurar que todos los guiones tengan estructura similar
   - Validar que incluya todos los elementos requeridos
   - Longitud apropiada (no muy corto ni muy largo)

4. **Cost Management**
   - Input: ~500 tokens (idea + prompt)
   - Output: ~3000 tokens (guion completo)
   - Coste estimado: ~0.020€ con Gemini 2.5 Pro

### Architecture Decisions

**Decision 1: Model Selection**
- **Options**: Gemini 2.5 Pro vs Gemini 2.5 Flash
- **Chosen**: Gemini 2.5 Pro
- **Rationale**:
  - Generación creativa requiere modelo premium
  - Flash (85/100) no suficiente para calidad de escritura
  - Pro (94/100) genera guiones más naturales y coherentes
  - Coste aceptable (~0.020€)

**Decision 2: Module Separation**
- **Options**: Integrar en `video_improver/` vs crear `script_generator/`
- **Chosen**: Integrar en `video_improver/` pero archivo separado
- **Rationale**:
  - Comparte configuración de Gemini
  - Reutiliza `config.py` y `report_generator.py`
  - Pero lógica completamente independiente
  - Fácil de mantener y testear separadamente

**Decision 3: Output Format**
- **Options**: Mismo formato que Video Analyzer vs formato específico
- **Chosen**: Formato específico para guiones
- **Rationale**:
  - Guion necesita secciones diferentes (intro, cuerpo, outro)
  - Incluir timestamps estimados
  - Sugerencias de B-roll y elementos visuales
  - Markdown pero estructura diferente

---

## High-level Task Breakdown

### Phase 0: Planning & Design (1 hour) ⏳
**Responsible**: Planner
**Dependencies**: None

**Subtasks**:
- [x] Definir estructura de guion objetivo
- [x] Diseñar prompt de generación
- [x] Estimar costes y tiempos
- [x] Crear este plan de implementación

**Success Criteria**:
- Plan aprobado por usuario
- Estructura de guion definida claramente
- Prompt base documentado

---

### Phase 1: Prompt Engineering & Testing (3 hours) ⏳
**Responsible**: Executor
**Dependencies**: Video Improvement Agent Phase 0 (setup de Gemini)

**Subtasks**:
- [ ] Crear `video_improver/script_generator.py`
- [ ] Diseñar prompt estructurado para generación de guiones
- [ ] Función `generate_script_from_idea(idea: str) -> GeneratedScript`
- [ ] Iterar en prompt con diferentes ejemplos
- [ ] Validar calidad de output (manual)
- [ ] Ajustar temperatura y parámetros de generación

**Success Criteria**:
- Genera guiones coherentes y bien estructurados
- Incluye todos los elementos requeridos
- Tono apropiado para YouTube
- Longitud 800-1200 palabras (~10-15 min lectura)

**Tests Required** (4 tests):
1. `test_generate_script_success` - Genera guion válido
2. `test_generate_script_structure` - Contiene secciones requeridas
3. `test_generate_script_length` - 800-1200 palabras
4. `test_generate_script_api_error` - Maneja errores API

**Prompt Base** (v1):
```python
SCRIPT_GENERATION_PROMPT = """
Eres un guionista profesional de YouTube experto en crear contenido educativo y entretenido.

Tu tarea es crear un guion completo de YouTube basado en la siguiente idea:
"{idea}"

El guion debe incluir:

1. **HOOK/GANCHO (0:00-0:15)**
   - Frase inicial impactante que capture atención
   - Presentación breve del tema
   - Por qué es importante/relevante

2. **INTRODUCCIÓN (0:15-1:00)**
   - Presentación personal (si aplica)
   - Contexto del tema
   - Qué aprenderá el espectador
   - CTA: pedir like y suscripción

3. **DESARROLLO/CUERPO (1:00-12:00)**
   - Dividir en 3-5 secciones claras
   - Cada sección con título descriptivo
   - Ejemplos prácticos y concretos
   - Transiciones suaves entre secciones
   - Mantener engagement (preguntas retóricas, humor, etc.)

4. **CONCLUSIÓN (12:00-14:00)**
   - Resumen de puntos clave
   - Takeaways accionables
   - CTA final (comentarios, siguiente video)

5. **OUTRO (14:00-15:00)**
   - Despedida
   - Recordatorio de like/suscripción
   - Teaser del próximo video (opcional)

REQUISITOS:
- Tono: Profesional pero accesible, conversacional
- Longitud: 800-1200 palabras (~10-15 minutos)
- Incluir timestamps estimados
- Sugerir 3-4 momentos para B-roll o elementos visuales
- Incluir 2-3 preguntas para engagement

FORMATO DE SALIDA:
Proporciona el guion en formato Markdown con:
- Títulos para cada sección
- Timestamps en formato [MM:SS]
- Notas de producción en _cursiva_ (ej: _mostrar gráfico aquí_)
- Textos para pantalla en **negrita** si aplica
"""
```

---

### Phase 2: SEO Optimization Integration (2 hours) ⏳
**Responsible**: Executor
**Dependencies**: Phase 1

**Subtasks**:
- [ ] Extender `generate_script_from_idea()` para incluir SEO
- [ ] Generar título optimizado (50-70 caracteres)
- [ ] Generar descripción SEO (150-200 palabras)
- [ ] Generar 15-20 tags relevantes
- [ ] Sugerir ideas de thumbnail
- [ ] Dataclass `GeneratedScript` con todos los campos

**Success Criteria**:
- Título SEO atractivo y optimizado
- Descripción incluye palabras clave
- Tags relevantes y específicos
- Ideas de thumbnail visuales y claras

**Tests Required** (5 tests):
1. `test_seo_title_length` - 50-70 caracteres
2. `test_seo_description_length` - 150-200 palabras
3. `test_seo_tags_count` - 15-20 tags
4. `test_seo_tags_relevance` - Tags relacionados con idea
5. `test_thumbnail_suggestions` - 3+ sugerencias

**Output Structure** (GeneratedScript):
```python
@dataclass
class GeneratedScript:
    # Guion
    script_text: str  # Guion completo en Markdown
    estimated_duration_minutes: int  # 10-15
    word_count: int  # 800-1200

    # SEO
    seo_title: str  # 50-70 caracteres
    seo_description: str  # 150-200 palabras
    seo_tags: list[str]  # 15-20 tags

    # Producción
    thumbnail_suggestions: list[str]  # Ideas de thumbnail
    broll_moments: list[tuple[str, str]]  # (timestamp, descripción)
    engagement_questions: list[str]  # Preguntas para engagement

    # Metadata
    generated_at: datetime
    model_used: str  # "gemini-2.5-pro"
    cost_usd: float  # Coste real
    raw_response: str  # Respuesta completa de Gemini
```

---

### Phase 3: CLI Implementation (2 hours) ⏳
**Responsible**: Executor
**Dependencies**: Phase 2

**Subtasks**:
- [ ] Añadir comando `generate-script` a `video_improver/cli.py`
- [ ] Argumentos: `--idea`, `--output`, `--format` (markdown/json)
- [ ] Mostrar estimación de coste antes de generar
- [ ] Progress spinner durante generación
- [ ] Guardar en `output_scripts/`

**Success Criteria**:
- CLI intuitiva y clara
- Acepta ideas multipalabra sin comillas
- Muestra preview del título generado
- Guarda en formato solicitado

**Tests Required** (4 tests):
1. `test_cli_generate_script_help` - Muestra ayuda
2. `test_cli_generate_script_missing_idea` - Error sin idea
3. `test_cli_generate_script_success` - E2E test
4. `test_cli_generate_script_formats` - Markdown y JSON

**CLI Usage**:
```bash
# Comando independiente
uv run python -m video_improver.cli generate-script \
  --idea "Video sobre cómo crear una aplicación Python con FastAPI con las mejores prácticas" \
  --output "output_scripts/fastapi_best_practices.md"

# Output esperado:
💡 Generando guion para: "Video sobre cómo crear una aplicación Python..."
💰 Coste estimado: 0.020€

[████████████████████] Generando guion...  ✓ (12s)
[████████████████████] Optimizando SEO...  ✓ (3s)

✅ Guion generado exitosamente
📄 Guardado en: output_scripts/fastapi_best_practices.md
📊 Estadísticas:
   - Palabras: 1,045
   - Duración estimada: 12 minutos
   - SEO: Título, descripción y 18 tags
   - Thumbnail: 4 sugerencias
💰 Coste real: 0.018€

🎬 Título generado: "FastAPI Masterclass: Guía Completa de Mejores Prácticas en Python"
```

---

### Phase 4: Report Formatting (1 hour) ⏳
**Responsible**: Executor
**Dependencies**: Phase 3

**Subtasks**:
- [ ] Crear template Markdown específico para guiones
- [ ] Secciones: Guion, SEO, Producción, Metadata
- [ ] Formato limpio y profesional
- [ ] Exportación opcional a JSON para automatización

**Success Criteria**:
- Markdown bien formateado
- Fácil de leer y copiar
- Incluye todos los elementos
- JSON válido si se solicita

**Tests Required** (3 tests):
1. `test_format_script_markdown` - Template correcto
2. `test_format_script_json` - JSON válido
3. `test_script_filename_sanitization` - Nombre de archivo limpio

**Template Markdown**:
```markdown
# 🎬 Guion Generado: {title}

**Generado**: {date}
**Duración estimada**: {duration} minutos
**Palabras**: {word_count}

---

## 📝 Guion Completo

{script_text_with_timestamps}

---

## 🎯 SEO & Optimización

### Título
{seo_title}

### Descripción
{seo_description}

### Tags
{seo_tags}

---

## 🎨 Notas de Producción

### Sugerencias de Thumbnail
1. {thumbnail_1}
2. {thumbnail_2}
3. {thumbnail_3}

### Momentos para B-roll
- [{timestamp}] {description}
...

### Preguntas de Engagement
- {question_1}
- {question_2}

---

## 📊 Metadata

- Modelo: {model_used}
- Coste: ${cost_usd}
- Generado: {timestamp}
```

---

### Phase 5: Testing & Validation (2 hours) ⏳
**Responsible**: Executor
**Dependencies**: Phase 4

**Subtasks**:
- [ ] Crear `test/test_script_generator.py`
- [ ] Tests unitarios para cada función
- [ ] Tests de integración E2E
- [ ] Validar calidad de scripts generados (manual)
- [ ] Probar con 10+ ideas diferentes
- [ ] Actualizar coverage

**Success Criteria**:
- Todos los tests pasan
- Coverage >70% en módulo script_generator
- Scripts generados son de calidad consistente
- No errores de formato o estructura

**Tests Required** (10 tests totales):
1. Unit tests: 7 (ya mencionados en fases anteriores)
2. Integration tests:
   - `test_e2e_script_generation_simple_idea`
   - `test_e2e_script_generation_complex_idea`
   - `test_e2e_script_generation_cost_validation`

---

## Project Status Board

### ✅ Completed Tasks
- [x] Análisis de requisitos
- [x] Diseño de arquitectura
- [x] Estimación de costes
- [x] Plan de implementación

### 🔄 In Progress
- [ ] Ninguna (esperando aprobación)

### 📋 To Do (Prioridad)
1. **BLOCKED**: Esperando completar Video Improvement Agent Phase 0 (setup de Gemini)
2. **HIGH**: Phase 1 - Prompt Engineering
3. **MEDIUM**: Phase 2 - SEO Integration
4. **MEDIUM**: Phase 3 - CLI Implementation
5. **LOW**: Phase 4 - Report Formatting
6. **LOW**: Phase 5 - Testing

### ⏸️ Blocked
- **Phase 1-5**: Requiere `google-generativeai` instalado (Video Improvement Agent Phase 0)

---

## Executor's Feedback or Assistance Requests

### Questions for Planner
*Ninguna aún - esperando aprobación del plan.*

### Blockers Encountered
*Ninguno aún - no iniciado.*

---

## Technical Specifications

### Dependencies (Same as Video Improvement Agent)
```toml
[project.dependencies]
google-generativeai = "^0.3.0"
rich = "^13.7.0"
```

### File Structure (Integrado en video_improver/)
```
video_improver/
├── __init__.py
├── cli.py                  # Añadir comando 'generate-script'
├── config.py               # Reutilizar configuración Gemini
├── script_generator.py     # NUEVO - Generación de guiones
├── models.py               # Añadir GeneratedScript dataclass
└── ...otros archivos...

output_scripts/             # NUEVO - Guiones generados
test/
└── test_video_improver/
    └── test_script_generator.py  # NUEVO
```

### Cost Breakdown (por guion)
| Component | Tokens | Cost per 1M | Total |
|-----------|--------|-------------|-------|
| Input (idea + prompt) | ~500 | $1.25 | ~$0.0006 |
| Output (guion completo) | ~3000 | $5.00 | ~$0.0150 |
| **TOTAL** | | | **~$0.0156** |

*Nota: Más barato que análisis de video porque no hay análisis visual.*

---

## Differences from Video Improvement Agent

### Key Differences

| Aspecto | Video Improver | Script Generator |
|---------|----------------|------------------|
| **Input** | Video file (mp4/mkv) | Text idea (string) |
| **Transcription** | Sí (Whisper) | No |
| **Visual Analysis** | Sí (Gemini Flash) | No |
| **Script Analysis** | Analítico (mejoras) | Creativo (generación) |
| **Output** | Mejoras de video existente | Guion nuevo desde cero |
| **Prompt** | Analítico y crítico | Creativo y generativo |
| **Cost** | ~0.025€ | ~0.016€ |
| **Time** | ~40 segundos | ~15 segundos |

### Shared Components
- ✅ Configuración de Gemini (`config.py`)
- ✅ Cliente de Gemini Pro
- ✅ Generación de reportes Markdown (template diferente)
- ✅ CLI con `rich` progress bars

---

## Risk Assessment

### High Risk
- **Calidad inconsistente**: Scripts pueden variar mucho
  - *Mitigation*: Iterar mucho en prompt engineering, validar con ejemplos

### Medium Risk
- **Ideas vagas**: Usuario da idea muy general
  - *Mitigation*: Prompt pide clarificación, ejemplos en documentación

### Low Risk
- **API Limits**: Mismo riesgo que Video Improver
  - *Mitigation*: Ya manejado en configuración compartida

---

## Next Steps

1. **Planner aprueba este plan** → Espera a Video Improver Phase 0
2. **Video Improver Phase 0 completa** → Executor inicia Script Generator Phase 1
3. **Usuario provee ideas de prueba** (5-10 ejemplos para validación)

---

## Notes

- Este feature es **completamente independiente** del análisis de videos
- Reutiliza infraestructura de Gemini pero **prompts diferentes**
- Puede desarrollarse **en paralelo** con Video Improver (después de Phase 0)
- Es **más rápido y más barato** que Video Improver
- Ideal para creadores que necesitan **inspiración y estructura**

---

**Última actualización**: 2025-01-03 (Planning Phase)
**Próxima revisión**: Después de Video Improvement Agent Phase 0
