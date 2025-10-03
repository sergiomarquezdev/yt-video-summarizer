.PHONY: help setup install test test-v test-cov test-cuda lint lint-fix format format-check typecheck check clean clean-all run update show-env

.DEFAULT_GOAL := help

# Detect operating system
ifeq ($(OS),Windows_NT)
	DETECTED_OS := Windows
	SHELL := cmd
	PYTORCH_INDEX := https://download.pytorch.org/whl/cu128
else
	UNAME_S := $(shell uname -s)
	ifeq ($(UNAME_S),Linux)
		DETECTED_OS := Linux
		PYTORCH_INDEX := https://download.pytorch.org/whl/cu128
	endif
	ifeq ($(UNAME_S),Darwin)
		DETECTED_OS := macOS
		PYTORCH_INDEX :=
	endif
endif

##@ Help

help: ## Show this help message
	@echo ======================================
	@echo yt-video-summarizer - Makefile
	@echo ======================================
	@echo.
	@echo Detected OS: $(DETECTED_OS)
	@echo.
	@echo Available targets:
	@echo.
	@echo Setup:
	@echo   make setup       - Complete development environment setup
	@echo   make install     - Alias for setup
	@echo.
	@echo Testing:
	@echo   make test        - Run all tests
	@echo   make test-v      - Run tests with verbose output
	@echo   make test-cov    - Run tests with coverage report
	@echo   make test-cuda   - Verify CUDA availability
	@echo.
	@echo Code Quality:
	@echo   make lint        - Run Ruff linter
	@echo   make lint-fix    - Run Ruff linter with auto-fix
	@echo   make format      - Format code with Ruff
	@echo   make format-check- Check code format
	@echo   make typecheck   - Run Mypy type checker
	@echo   make check       - Run all quality checks
	@echo.
	@echo Development:
	@echo   make run URL="..." - Run CLI with URL
	@echo.
	@echo Cleanup:
	@echo   make clean       - Remove temp files and caches
	@echo   make clean-all   - Remove temp files and venv
	@echo.
	@echo Utilities:
	@echo   make update      - Update dependencies
	@echo   make show-env    - Show Python environment info
	@echo.

##@ Setup & Installation

setup: ## Complete development environment setup (cross-platform)
	@echo.
	@echo ======================================
	@echo   Development Environment Setup
	@echo ======================================
	@echo.
	@echo Detected OS: $(DETECTED_OS)
	@echo.
	@echo [1/7] Checking UV installation...
	@uv --version > nul 2>&1 || (echo ERROR: UV not found. Install it first: && echo   Windows: powershell -c "irm https://astral.sh/uv/install.ps1 | iex" && echo   Linux/macOS: curl -LsSf https://astral.sh/uv/install.sh | sh && exit 1)
	@echo   UV is installed
	@echo.
	@echo [2/7] Creating virtual environment...
	@uv venv --python 3.13
	@echo   Virtual environment created
	@echo.
	@echo [3/7] Installing dependencies...
	@uv sync --extra dev
	@echo   Dependencies installed
	@echo.
ifeq ($(DETECTED_OS),macOS)
	@echo [4/7] Skipping PyTorch CUDA (macOS uses MPS)...
	@echo   Note: macOS M1/M2 chips use Metal Performance Shaders (MPS)
	@echo   PyTorch will use CPU/MPS automatically
else
	@echo [4/7] Installing PyTorch with CUDA support...
	@uv pip install torch torchvision torchaudio --index-url $(PYTORCH_INDEX) --force-reinstall
	@echo   PyTorch CUDA installed
endif
	@echo.
	@echo [5/7] Verifying installation...
	@uv run python test/check_pytorch_cuda.py
	@echo.
	@echo [6/7] Running test suite...
	@uv run pytest -q
	@echo.
	@echo [7/7] Installing pre-commit hooks...
	@uv run pre-commit install
	@echo.
	@echo ======================================
	@echo   Setup Complete!
	@echo ======================================
	@echo   Pre-commit hooks installed
	@echo   Run 'make help' to see all commands
	@echo ======================================
	@echo.

install: setup ## Alias for 'make setup'

##@ Development

run: ## Run the CLI (set URL=<youtube-url>)
	@if not defined URL (echo Usage: make run URL=https://www.youtube.com/watch?v=VIDEO_ID && uv run python -m yt_transcriber.cli --help) else (uv run python -m yt_transcriber.cli --url "$(URL)")

##@ Testing

test: ## Run all tests
	uv run pytest

test-v: ## Run tests with verbose output
	uv run pytest -v

test-cov: ## Run tests with coverage report
	uv run pytest --cov=yt_transcriber --cov-report=html --cov-report=term

test-cuda: ## Verify CUDA availability
	uv run python test/check_pytorch_cuda.py

##@ Code Quality

lint: ## Run linter (Ruff check)
	uv run ruff check .

lint-fix: ## Run linter and auto-fix issues
	uv run ruff check --fix .

format: ## Format code with Ruff
	uv run ruff format .

format-check: ## Check code formatting without modifying files
	uv run ruff format --check .

typecheck: ## Run type checker (Mypy)
	uv run mypy --package yt_transcriber

check: lint format-check typecheck test ## Run all quality checks (lint + format + typecheck + test)
	@echo.
	@echo All checks passed!

##@ Cleanup

clean: ## Remove temporary files and caches
	@echo Cleaning temporary files...
	@if exist temp_files rmdir /s /q temp_files 2>nul
	@if exist .pytest_cache rmdir /s /q .pytest_cache 2>nul
	@if exist .ruff_cache rmdir /s /q .ruff_cache 2>nul
	@if exist .mypy_cache rmdir /s /q .mypy_cache 2>nul
	@if exist htmlcov rmdir /s /q htmlcov 2>nul
	@if exist .coverage del /f /q .coverage 2>nul
	@for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d" 2>nul
	@for /d /r . %%d in (*.egg-info) do @if exist "%%d" rmdir /s /q "%%d" 2>nul
	@echo Cleanup complete.

clean-all: clean ## Remove temporary files AND virtual environment
	@echo Removing virtual environment...
	@if exist .venv rmdir /s /q .venv 2>nul
	@if exist uv.lock del /f /q uv.lock 2>nul
	@echo Full cleanup complete.

##@ Utilities

update: ## Update dependencies to latest versions
	uv sync --upgrade

show-env: ## Show Python environment information
	@echo.
	@echo Python Environment Information:
	@echo.
	@uv run python --version
	@echo.
	@uv run python -c "import sys; print(f'Executable: {sys.executable}')"
