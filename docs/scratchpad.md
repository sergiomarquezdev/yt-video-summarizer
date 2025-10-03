# Scratchpad - Desarrollo Activo

## Current Task

🎯 **Feature**: Video Summarization con IA
📅 **Fecha inicio**: 2025-10-03
📊 **Estado**: ✅ Planning Complete → Ready for Execution
🔗 **Plan detallado**: [implementation-plan/video-summarization.md](implementation-plan/video-summarization.md)

### User Requirements (Confirmados)

- ✅ Transcripción + Resumen SIEMPRE generados juntos (2 archivos)
- ✅ Sin checkbox, sin opciones - automático como EN/ES scripts
- ✅ Timestamps siempre incluidos
- ✅ Nivel "detailed" fijo
- ✅ Solo idiomas ES/EN (simplificar UI)
- ✅ Formato Markdown único

## Lessons Learned### [2025-10-03] Configuración inicial

- Proyecto usa UV como package manager (10-100x más rápido que pip)
- PyTorch CUDA requiere instalación manual después de `uv sync` debido a índice personalizado
- Pre-commit hooks configurados pero se pueden saltar con `--no-verify` si hay problemas
- Gradio 5.0+ tiene soporte nativo para async, no necesita Celery para operaciones en background
- Git workflow: siempre verificar `git status` antes y después de commits

### [2025-10-03] UI/UX Design

- Tema dark personalizado basado en One Daily Blog (#0f172a, #1e293b, #22d3ee)
- CSS mínimo es mejor que CSS complejo - 14 líneas son suficientes
- Gap de 2rem entre columnas mejora legibilidad significativamente
- Eliminar archivos temporales de implementación antes de commit final

## Active Branches

- `main`: Rama principal (protegida)
- Próximo: `feature/video-summarization`

## Quick Commands

```bash
# Setup
make setup

# Run web interface
make start

# Tests
make test
make test-cov

# Code quality
make check
make lint-fix
make format

# Git workflow
git status
git add .
git commit -m "mensaje"
git push
```

## Environment Setup

- Python 3.13
- CUDA 12.8 (NVIDIA GPU)
- Whisper model: base (por defecto)
- Gemini API: Configurado y funcionando
- YouTube Data API v3: Configurado

## Current Architecture

```
yt_transcriber/
├── cli.py              # Entry point con subcommands
├── config.py           # Pydantic settings
├── downloader.py       # YouTube download
├── transcriber.py      # Whisper transcription
└── utils.py            # Shared utilities

youtube_script_generator/
├── models.py           # Dataclasses
├── query_optimizer.py  # Gemini query optimization
├── youtube_searcher.py # YouTube search
├── batch_processor.py  # Parallel processing
├── pattern_analyzer.py # Pattern extraction
├── synthesizer.py      # Pattern aggregation
├── script_generator.py # Script generation
└── translator.py       # EN→ES translation

frontend/
├── gradio_app.py       # Web UI (Gradio)
└── README.md           # UI documentation
```

## Next Steps - EXECUTION MODE

### PHASE 1: Core Implementation (2h estimado)

1. ⏳ Crear dataclasses en `youtube_script_generator/models.py`
2. ⏳ Implementar `yt_transcriber/summarizer.py`
3. ⏳ Actualizar `config.py` con settings
4. ⏳ Tests unitarios básicos

### PHASE 2: CLI Integration (1h estimado)

5. ⏳ Modificar `cli.py` - función `transcribe_video_ui()`
6. ⏳ Wrapper que genera transcripción + resumen
7. ⏳ Tests de integración CLI

### PHASE 3: Gradio UI Integration (1h estimado)

8. ⏳ Modificar `frontend/gradio_app.py`
9. ⏳ Añadir output adicional para resumen
10. ⏳ Simplificar dropdowns (solo ES/EN)
11. ⏳ Tests manuales UI

### PHASE 4: Testing & Documentation (1.5h estimado)

12. ⏳ Suite completa de tests
13. ⏳ Actualizar README.md
14. ⏳ Actualizar frontend/README.md
15. ⏳ Actualizar AGENTS.md

### PHASE 5: Polish & Deployment (0.5h estimado)

16. ⏳ Linting y formatting
17. ⏳ Type checking (Mypy)
18. ⏳ Coverage check
19. ⏳ Git commit & push

**Total estimado**: 6 horas
**Progreso**: 0/19 tareas completadas 7. ⏳ Commit y push

---

_Última actualización: 2025-10-03 18:30_
