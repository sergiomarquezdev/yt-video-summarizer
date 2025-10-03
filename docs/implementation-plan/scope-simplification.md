# Video Summarization - Simplificación del Scope

**Fecha**: 2025-10-03 18:45  
**Decisión**: User feedback - simplificar implementación

## ❌ Removido del Scope Original

### UI Changes
- ❌ Checkbox "Generar resumen automático" 
- ❌ Accordion con opciones de configuración
- ❌ Radio "Breve/Detallado"
- ❌ Dropdown multi-idioma (FR, DE, PT, IT, JA, etc.)
- ❌ Toggle de timestamps

### CLI Changes
- ❌ Subcommand separado `summarize`
- ❌ Opciones `--detail`, `--no-timestamps`, `--format`
- ❌ Formatos TXT/JSON (solo Markdown)

### Code Complexity
- ❌ Lógica condicional para checkbox
- ❌ Templates "brief" vs "detailed"
- ❌ Multi-language prompts (solo ES/EN)
- ❌ Export formats (solo MD)

## ✅ Nuevo Scope Simplificado

### Behavior
✅ **Transcripción automática** → Genera 2 archivos:
   - `{video}_transcript.txt` (existente)
   - `{video}_summary.md` (NUEVO)

✅ **Siempre ejecutado** - Sin opciones, sin configuración

✅ **Fixed settings**:
   - Nivel: Detallado (fixed)
   - Timestamps: Incluidos (fixed)
   - Idioma: Auto-detect ES/EN (fixed)
   - Format: Markdown (fixed)

### UI Changes (Minimal)
✅ Añadir output adicional en columna izquierda:
   - Transcription output (existente)
   - Transcription file download (existente)
   - **Summary preview** (NUEVO - Markdown renderizado)
   - **Summary file download** (NUEVO)

✅ Simplificar dropdowns existentes:
   - "Auto-detectar" → Solo "Español" y "English"
   - Eliminar FR, DE, PT, IT de todas partes

### CLI Changes (Minimal)
✅ Modificar `transcribe` command:
   - Mismo comando, sin cambios en argumentos
   - Internamente genera transcripción + resumen
   - Output: 2 archivos automáticamente

✅ No nuevo subcommand

## 📊 Impact Analysis

### Código Reducido
- **Antes**: ~800 líneas nuevas estimadas
- **Ahora**: ~400 líneas nuevas estimadas
- **Ahorro**: 50% menos complejidad

### Tiempo de Desarrollo
- **Antes**: 6-7 horas
- **Ahora**: 4-5 horas
- **Ahorro**: ~2 horas

### Mantenimiento
- **Antes**: Múltiples code paths, configuraciones, opciones
- **Ahora**: Single path, zero configuration
- **Beneficio**: Menos bugs, más fácil de mantener

### User Experience
- **Antes**: Usuario debe activar checkbox, elegir opciones
- **Ahora**: Zero friction - funciona automáticamente
- **Beneficio**: Más simple = mejor UX

## 🎯 Implementation Changes

### Files to Create
- `yt_transcriber/summarizer.py` (NUEVO)
- `test/test_summarizer.py` (NUEVO)

### Files to Modify
- `youtube_script_generator/models.py` - Añadir VideoSummary dataclass
- `yt_transcriber/config.py` - Añadir SUMMARIZER_MODEL, SUMMARY_OUTPUT_DIR
- `yt_transcriber/cli.py` - Modificar run_transcribe_command() para generar resumen
- `frontend/gradio_app.py` - Añadir outputs, simplificar dropdowns
- `README.md` - Documentar nueva funcionalidad
- `frontend/README.md` - Actualizar
- `AGENTS.md` - Actualizar arquitectura

### Prompts Needed
- Solo 1 prompt (español/inglés detectado automáticamente)
- Nivel "detailed" fixed
- Timestamps fixed
- Sin variaciones

## ✅ Success Criteria (Simplified)

### MVP
- ✅ `transcribe` command genera 2 archivos automáticamente
- ✅ Summary con formato correcto (detailed, con timestamps)
- ✅ Preview en Gradio UI
- ✅ Descarga de ambos archivos

### Full Feature
- ✅ Detección automática ES/EN
- ✅ Tests >60% coverage
- ✅ Documentación completa
- ✅ Zero configuración necesaria

## 📝 Example Output

```bash
# Usuario ejecuta (sin cambios):
python -m yt_transcriber.cli transcribe -u "https://youtube.com/..."

# Output (NUEVO - 2 archivos):
✅ Transcription saved: output_transcripts/VideoTitle_transcript.txt
✅ Summary saved: output_summaries/VideoTitle_summary.md
```

**Gradio UI**: Same single button, pero devuelve 2 archivos descargables.

---

**Aprobado por**: Usuario  
**Next action**: Pasar a modo Executor - Phase 1
