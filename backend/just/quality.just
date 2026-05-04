[group("Quality")]
[doc("Run Ruff lint checks")]
lint: _uv-ready
    uv run ruff check src

[group("Quality")]
[doc("Run Ruff format checks")]
format-check: _uv-ready
    uv run ruff format --check src

[group("Quality")]
[doc("Run static type checks")]
typecheck: _uv-ready
    uv run ty check

[group("Quality")]
[doc("Run all configured quality checks")]
quality: lint format-check typecheck
    @echo "[quality] All quality checks passed"
