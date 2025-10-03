# Gradio Web Interface

Interfaz web simple para **YouTube Video Transcriber & Script Generator** usando Gradio.

## 🚀 Inicio Rápido

### Opción 1: Makefile (Recomendado)

```bash
make start
```

Esto iniciará el servidor en `http://localhost:7860` y abrirá automáticamente el navegador.

### Opción 2: Comando directo

```bash
uv run python frontend/gradio_app.py
```

## 🎨 Características

### Columna Izquierda: Transcribir Video de YouTube

- **URL de YouTube**: Pega la URL completa del video
- **Idioma**: Selecciona el idioma o deja en "Auto-detectar"
- **Ruta FFmpeg**: Solo si FFmpeg no está en PATH (opcional)
- **Botón Transcribir**: Inicia el proceso de transcripción
- **Resultado**: Muestra el estado y ruta del archivo generado
- **Descarga**: Descarga directamente la transcripción en formato `.txt`

### Columna Derecha: Generar Guión de YouTube

- **Idea del Video**: Describe el tema del video que quieres crear
- **Max Videos**: Número de videos a analizar (5-20)
- **Duración Objetivo**: Duración deseada del guión final en minutos (5-30)
- **Estilo**: Define el tono (opcional, ej: "casual", "educativo")
- **Botón Generar**: Inicia el pipeline completo de 7 fases
- **Resultado**: Muestra estadísticas del proceso
- **Descargas**: Descarga guiones en inglés (EN) y español (ES)

## 🔧 Configuración

La interfaz lee automáticamente la configuración de `.env`:

```env
# Modelo Whisper
WHISPER_MODEL_NAME=base          # tiny, base, small, medium, large
WHISPER_DEVICE=cuda              # cuda, cpu

# API de Gemini (Script Generator)
GOOGLE_API_KEY=tu_api_key_aqui

# Directorios de salida
OUTPUT_DIR=output_transcripts
OUTPUT_SCRIPTS_DIR=output_scripts
OUTPUT_ANALYSIS_DIR=output_analysis
```

## ⚡ Rendimiento

### Transcripción de Video

- **Entrada**: URL de YouTube
- **Tiempo**: 2-5 minutos (depende de la duración del video y GPU)
- **Modelo**: Whisper (base/medium/large) con aceleración CUDA
- **Salida**: Archivo `.txt` con la transcripción

### Generación de Guión

- **Entrada**: Idea del video + parámetros
- **Tiempo**: 8-15 minutos para 10 videos
- **Pipeline**: 7 fases (Query → Search → Download → Transcribe → Analyze → Synthesize → Generate → Translate)
- **Salida**: 2 archivos `.md` (inglés + español) + reporte de síntesis

## 📝 Notas Técnicas

### Progress Bars

Gradio muestra automáticamente progress bars durante las operaciones largas:

- Descarga de videos
- Transcripción con Whisper
- Llamadas a Gemini API
- Traducción al español

### Manejo de Errores

La interfaz captura y muestra errores de forma clara:

- ❌ URL inválida
- ❌ FFmpeg no encontrado
- ❌ Fallo en descarga
- ❌ Error en transcripción
- ❌ API key de Gemini inválida

### Logs

Los logs detallados se muestran en la terminal donde ejecutaste `make start`:

```
2025-10-03 15:30:45 - yt_transcriber.downloader - INFO - Downloading video: https://...
2025-10-03 15:31:12 - yt_transcriber.transcriber - INFO - Transcribing audio...
2025-10-03 15:33:45 - yt_transcriber.cli - INFO - Transcription completed
```

## 🌐 Acceso Remoto

Para permitir acceso desde otros dispositivos en tu red local:

1. Edita `frontend/gradio_app.py`
2. Cambia `share=False` a `share=True` en `app.launch()`
3. Gradio generará una URL pública temporal (válida por 72h)

```python
app.launch(
    server_name="0.0.0.0",
    server_port=7860,
    share=True,  # ← Cambia esto
    inbrowser=True,
)
```

## 🛑 Detener el Servidor

Presiona `Ctrl+C` en la terminal para detener el servidor Gradio.

## 🐛 Troubleshooting

### El navegador no se abre automáticamente

Abre manualmente: http://localhost:7860

### Puerto 7860 ya en uso

Cambia el puerto en `frontend/gradio_app.py`:

```python
app.launch(
    server_port=8080,  # ← Cambia a otro puerto
    # ...
)
```

### Operación muy lenta

- **Transcripción**: Usa modelo `base` en vez de `medium`/`large`
- **Script Generator**: Reduce `max_videos` de 10 a 5

### Error "CUDA not available"

La interfaz funcionará con CPU, pero será más lenta. Verifica:

```bash
uv run python test/check_pytorch_cuda.py
```

## 📚 Documentación Adicional

- [AGENTS.md](../AGENTS.md) - Documentación técnica completa
- [README.md](../README.md) - Uso general del proyecto
- [docs/YOUTUBE_SCRIPT_GENERATOR.md](../docs/YOUTUBE_SCRIPT_GENERATOR.md) - Pipeline de generación de guiones
