# Scratchpad - yt-video-summarizer

## Active Tasks

### 1. ✅ COMPLETED: Project Audit & Quality Improvements

**Status**: ✅ Completado (2025-01-03)
**Implementation Plan**: N/A (inicial audit)
**Summary**:

- Auditoría completa del proyecto
- Creación de 31 tests de integración (49 totales, 59% coverage)
- Migración de Pydantic v1 → v2 (0 warnings)
- Proyecto en estado excelente (9.5/10)

---

### 2. 🔄 IN PROGRESS: YouTube-Powered Script Generator

**Status**: 🔄 Planning Phase
**Implementation Plan**: [docs/implementation-plan/youtube-script-generator.md](./implementation-plan/youtube-script-generator.md)
**Summary**:
Sistema inteligente que genera guiones optimizados aprendiendo de videos exitosos en YouTube:

**Flujo completo:**

1. Usuario proporciona idea: "crear proyecto con FastAPI en Python"
2. Sistema optimiza query de búsqueda con Gemini
3. Busca top 15 videos en YouTube con yt-dlp
4. Transcribe todos los videos con Whisper (CUDA)
5. Analiza cada video extrayendo patrones (hooks, CTAs, estructura)
6. Sintetiza los 15 análisis en un documento de mejores prácticas
7. Genera guión optimizado usando síntesis como contexto

**Tech Stack:**

- ✅ yt-dlp (YouTube search + metadata) - Gratis
- ✅ Gemini 2.5 Pro (query optimization, análisis, síntesis, generación) - ~0.16€
- ✅ Whisper local (transcripción CUDA) - Gratis
- ✅ Total: ~0.16€ por guión completo

**Ventajas clave:**

- Siempre actualizado (analiza videos actuales)
- Contexto perfectamente relevante (tema exacto)
- No requiere base de datos ni mantenimiento
- Calidad esperada: 90-95/100

---

### 3. ⏸️ ARCHIVED: Video Improvement Agent (Local Analysis)

**Status**: ⏸️ Archivado (enfoque cambiado)
**Razón**: Pivote a solución más simple y efectiva (YouTube-Powered Script Generator)
**Plan original**: [docs/implementation-plan/video-improvement-agent.md](./implementation-plan/video-improvement-agent.md)

---

### 4. ⏸️ ARCHIVED: Script Generator from Idea (RAG-based)

**Status**: ⏸️ Archivado (enfoque cambiado)
**Razón**: RAG innecesario, síntesis contextual es más efectiva
**Plan original**: [docs/implementation-plan/script-generator-from-idea.md](./implementation-plan/script-generator-from-idea.md)

---

## Project Evolution Timeline

### 2025-01-03 - Initial Vision

- Analizador de videos locales + Generador de guiones
- RAG con ChromaDB/Pinecone para almacenar patrones

### 2025-01-03 - First Pivot

- Descartamos videos locales (no prioritario)
- Enfoque en YouTube → RAG → Script Generator
- Preocupación: ¿Cómo query RAG devuelve técnicas vs contenido?

### 2025-01-03 - Second Pivot (FINAL)

- **Insight clave**: En lugar de RAG estático, análisis contextual dinámico
- Buscar videos del tema exacto → Sintetizar → Generar
- Ventajas: Siempre actualizado, perfectamente relevante, zero mantenimiento

---

## Lessons Learned

### [2025-01-03] Pydantic V2 Migration

- **Problema**: Warnings de sintaxis deprecated v1
- **Solución**: Migrar a `Field(default=)` y `SettingsConfigDict`
- **Resultado**: 0 warnings, mejor performance

### [2025-01-03] Test Philosophy - Quality over Quantity

- **Problema**: Intentar forzar 100% coverage con tests frágiles
- **Solución**: Enfocarse en critical paths, evitar over-mocking
- **Resultado**: 59% coverage pragmático, tests rápidos y estables

### [2025-01-03] LLM Selection - Cost/Quality Analysis

- **Contexto**: Comparar Claude 3.5 Sonnet vs Gemini 2.5 Pro
- **Descubrimiento**: Gemini 2.5 Pro es 2.7x más barato (0.024€ vs 0.068€) con calidad superior (94/100 vs 92/100)
- **Decisión**: Usar estrategia híbrida Gemini (Flash + Pro) para análisis completo
- **Beneficios adicionales**: Multimodal nativo, tier gratuito 1500 req/día, contexto 2M tokens

### [2025-01-03] Architecture Decision - Dynamic Context vs Static RAG

- **Contexto**: ¿RAG con base de datos o síntesis contextual bajo demanda?
- **Descubrimiento**: Síntesis contextual es superior para este caso de uso
- **Razones**:
  - Siempre analiza videos actuales del tema exacto
  - No requiere mantenimiento de base de datos
  - Contexto perfectamente relevante (no aproximado)
  - Zero staleness (RAG puede quedar obsoleto)
- **Decisión**: YouTube search → Transcribe → Analyze → Synthesize → Generate
- **Trade-off aceptado**: +10 min tiempo ejecución vs RAG (30 seg), pero calidad superior

### [2025-01-03] Tool Selection - yt-dlp vs YouTube API

- **Contexto**: ¿Cómo obtener videos de YouTube para análisis?
- **Opciones evaluadas**:
  - YouTube Data API v3: Oficial, 10K units/día gratis (100 búsquedas/día)
  - yt-dlp: Scraping inteligente, sin límites, más metadata
- **Decisión**: yt-dlp para MVP
- **Razones**:
  - Sin límites de cuota (YouTube API limitado)
  - Más información (views, likes, duración exacta, fecha)
  - Ya instalado como dependencia
  - Gratis completamente
- **Fallback posible**: Hybrid con YouTube API si yt-dlp falla

---

## Quick Links

- [AGENTS.md](../AGENTS.md) - Project documentation for AI agents
- [README.md](../README.md) - User-facing documentation
- [Implementation Plans](./implementation-plan/) - Detailed task breakdowns

---

## Notes

- Seguimos filosofía TDD: tests primero, código después
- Priorizar simplicidad sobre ingeniería excesiva
- Documentar lecciones aprendidas inmediatamente
- Commits pequeños y focalizados
