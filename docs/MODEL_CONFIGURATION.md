# Configuración de Modelos Gemini - Optimizada para Calidad y Costo

> **Última actualización:** 3 de octubre, 2025
> **Filosofía:** "Modelo SUFICIENTE" - Elegir el modelo más económico que entregue calidad suficiente para cada tarea

---

## 📊 Resumen de Modelos Configurados

| Modelo                    | Uso                                                   | Costo (Input/Output)         | Justificación                                                      |
| ------------------------- | ----------------------------------------------------- | ---------------------------- | ------------------------------------------------------------------ |
| **gemini-2.5-pro**        | Synthesis + Script Generation                         | $2.50 / $15.00 por 1M tokens | **CRÍTICO** - Producto final, necesita máxima calidad              |
| **gemini-2.5-flash**      | Summarization + Pattern Analysis + Script Translation | GRATIS (free tier)           | Excelente calidad, thinking capabilities, suficiente para análisis |
| **gemini-2.5-flash-lite** | Summary Translation + Query Optimization              | $0.075 / $0.30 por 1M tokens | Tareas simples, modelo ligero suficiente                           |

---

## 🎯 Configuración por Escenario

### Escenario 1: Video → Resumen → Traducción

```python
# 1. Transcripción (Whisper local GPU)
WHISPER_MODEL_NAME = "medium"  # Local, gratis

# 2. Resumen del video
SUMMARIZER_MODEL = "gemini-2.5-flash"  # Free tier, excelente calidad

# 3. Traducción del resumen (EN → ES)
TRANSLATOR_MODEL = "gemini-2.5-flash-lite"  # Traducción simple, lite suficiente
```

**Costo Total: ~$0.00** (free tier) ✅

---

### Escenario 2: Query → Videos → Script → Traducción

```python
# 1. Query Optimization
QUERY_OPTIMIZER_MODEL = "gemini-2.5-flash-lite"  # Tarea simple

# 2. Pattern Analysis (10 videos)
PATTERN_ANALYZER_MODEL = "gemini-2.5-flash"  # Free tier, suficiente para análisis estructurado

# 3. Pattern Synthesis
GEMINI_PRO_MODEL = "gemini-2.5-pro"  # CRÍTICO - Sintetizar 10 análisis

# 4. Script Generation
GEMINI_PRO_MODEL = "gemini-2.5-pro"  # CRÍTICO - Producto final

# 5. Script Translation (EN → ES)
SUMMARIZER_MODEL = "gemini-2.5-flash"  # Debe preservar estilo, flash necesario
```

**Costo Total: ~$0.105 por script** (~11¢) ✅

---

## 💰 Desglose de Costos (Escenario 2 - Script Generation)

### Entrada (Input Tokens)

| Tarea                  | Tokens | Modelo     | Costo      |
| ---------------------- | ------ | ---------- | ---------- |
| Query Optimization     | 500    | flash-lite | $0.00004   |
| Pattern Analysis (10x) | 30,000 | flash      | **GRATIS** |
| Synthesis              | 12,000 | pro        | $0.030     |
| Script Generation      | 3,000  | pro        | $0.0075    |
| Translation            | 2,500  | flash      | **GRATIS** |
| **SUBTOTAL INPUT**     |        |            | **$0.037** |

### Salida (Output Tokens)

| Tarea                  | Tokens | Modelo     | Costo      |
| ---------------------- | ------ | ---------- | ---------- |
| Query Optimization     | 200    | flash-lite | $0.00006   |
| Pattern Analysis (10x) | 10,000 | flash      | **GRATIS** |
| Synthesis              | 2,000  | pro        | $0.030     |
| Script Generation      | 2,500  | pro        | $0.0375    |
| Translation            | 2,500  | flash      | **GRATIS** |
| **SUBTOTAL OUTPUT**    |        |            | **$0.068** |

### Total por Script

**Input + Output = $0.105** (~11¢)

---

## 📋 Configuración en Código

### En `yt_transcriber/config.py`

```python
class AppSettings(BaseSettings):
    # ========== GEMINI MODEL CONFIGURATION ==========

    # For script synthesis and generation (CRITICAL - needs max quality)
    GEMINI_PRO_MODEL: str = Field(
        default="gemini-2.5-pro",
        description="Modelo premium para synthesis y script generation ($2.50/$15.00)",
    )

    # For video summarization (balanced quality, free tier)
    SUMMARIZER_MODEL: str = Field(
        default="gemini-2.5-flash",
        description="Modelo para resúmenes de video (free tier, excelente calidad)",
    )

    # For pattern analysis from transcripts (10 videos, free tier)
    PATTERN_ANALYZER_MODEL: str = Field(
        default="gemini-2.5-flash",
        description="Modelo para análisis de patrones (free tier, suficiente calidad)",
    )

    # For translations (summaries use lite, scripts use flash)
    TRANSLATOR_MODEL: str = Field(
        default="gemini-2.5-flash-lite",
        description="Modelo para traducciones simples ($0.075/$0.30)",
    )

    # For simple tasks (query optimization)
    QUERY_OPTIMIZER_MODEL: str = Field(
        default="gemini-2.5-flash-lite",
        description="Modelo para optimización de queries ($0.075/$0.30)",
    )
```

---

## 🔧 Uso en el Código

### PatternAnalyzer (`youtube_script_generator/pattern_analyzer.py`)

```python
# Usa PATTERN_ANALYZER_MODEL (gemini-2.5-flash)
analyzer = PatternAnalyzer()  # Default: settings.PATTERN_ANALYZER_MODEL
```

### QueryOptimizer (`youtube_script_generator/query_optimizer.py`)

```python
# Usa QUERY_OPTIMIZER_MODEL (gemini-2.5-flash-lite)
optimizer = QueryOptimizer()  # Default: settings.QUERY_OPTIMIZER_MODEL
```

### PatternSynthesizer (`youtube_script_generator/synthesizer.py`)

```python
# Usa GEMINI_PRO_MODEL (gemini-2.5-pro)
synthesizer = PatternSynthesizer()  # Default: settings.GEMINI_PRO_MODEL
```

### ScriptGenerator (`youtube_script_generator/script_generator.py`)

```python
# Usa GEMINI_PRO_MODEL (gemini-2.5-pro)
generator = ScriptGenerator()  # Default: settings.GEMINI_PRO_MODEL
```

### ScriptTranslator (`youtube_script_generator/translator.py`)

```python
# Para resúmenes: usa TRANSLATOR_MODEL (gemini-2.5-flash-lite)
translator = ScriptTranslator(use_translation_model=True)

# Para scripts: usa SUMMARIZER_MODEL (gemini-2.5-flash)
translator = ScriptTranslator(use_translation_model=False)
```

### VideoSummarizer (`yt_transcriber/summarizer.py`)

```python
# Usa SUMMARIZER_MODEL (gemini-2.5-flash)
summary = generate_summary(transcript)  # Función usa settings.SUMMARIZER_MODEL
```

---

## ⚠️ Punto de Atención: Pattern Analysis

**Configuración Actual:** `gemini-2.5-flash` (gratis)

**Riesgo Potencial:**

- Flash puede perder patrones sutiles comparado con Pro
- Análisis menos profundo que Pro
- Si la calidad del script no es suficiente, considerar upgrade

**Opción de Upgrade:**

```python
# En config.py, cambiar a:
PATTERN_ANALYZER_MODEL = "gemini-2.5-pro"

# Costo adicional: +$0.225 por script
# Costo total con upgrade: $0.33 por script
```

**Recomendación:**

1. ✅ Empezar con `2.5-flash` ($0.105/script)
2. ✅ Generar 2-3 scripts de prueba
3. ✅ Si la calidad es suficiente → mantener Flash
4. ⚠️ Si falta profundidad → upgrade a Pro

---

## 🎯 Presupuestos Originales vs Configuración Final

| Escenario                    | Presupuesto | Costo Actual | Estado                   |
| ---------------------------- | ----------- | ------------ | ------------------------ |
| Video (resumen + traducción) | <$0.05      | **$0.00**    | ✅ Muy por debajo        |
| Script (generación completa) | <$0.15      | **$0.105**   | ✅ Dentro de presupuesto |

**Margen de seguridad:**

- Video: $0.05 de margen
- Script: $0.045 de margen (~4.5¢ libre para ajustes)

---

## 🔄 Historial de Cambios

### v3.0 - 3 octubre 2025 (Configuración "Suficiente")

- ✅ Centralizada toda la configuración en `config.py`
- ✅ Añadido `PATTERN_ANALYZER_MODEL` (gemini-2.5-flash)
- ✅ Añadido `QUERY_OPTIMIZER_MODEL` (gemini-2.5-flash-lite)
- ✅ Actualizado `GEMINI_PRO_MODEL` → gemini-2.5-pro (desde 1.5-pro)
- ✅ Actualizado `TRANSLATOR_MODEL` → gemini-2.5-flash-lite (desde 1.5-flash-8b)
- ✅ Mantenido `SUMMARIZER_MODEL` → gemini-2.5-flash
- ✅ Costo final: $0.105 por script (dentro de presupuesto)

### v2.0 - 2 octubre 2025 (Multi-modelo)

- Añadido soporte para modelos múltiples
- Creado `TRANSLATOR_MODEL` separado
- Implementada traducción bilingüe (EN+ES)

### v1.0 - 1 octubre 2025 (Inicial)

- Configuración básica con gemini-1.5-pro
- Sin optimización de costos

---

## 🚀 Próximos Pasos

1. **Testing en Producción:**

   ```bash
   # Test Escenario 1
   uv run python -m yt_transcriber.cli transcribe -u "https://youtube.com/watch?v=VIDEO_ID"

   # Test Escenario 2
   uv run python -m yt_transcriber.cli generate-script --idea "Python tutorial" --max-videos 5
   ```

2. **Validar Calidad:**

   - Revisar resúmenes generados
   - Evaluar calidad de scripts
   - Verificar traducciones al español

3. **Monitorear Costos:**

   - Google AI Studio dashboard
   - Verificar uso del free tier
   - Confirmar costos de Pro en scripts

4. **Ajustar si Necesario:**
   - Si Pattern Analysis es insuficiente → upgrade a Pro
   - Si traducciones tienen errores → upgrade a Flash
   - Documentar resultados en este archivo

---

## 📚 Referencias

- **Documentación Oficial:** https://ai.google.dev/gemini-api/docs/models/gemini
- **Precios:** https://ai.google.dev/pricing
- **API Key:** https://aistudio.google.com/apikey
- **Límites Free Tier:**
  - 2.5-flash: 15 RPM, 1M tokens/día
  - 2.5-pro: 2 RPM (paid tier)
