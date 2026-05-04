[group("Help")]
[doc("Show grouped just commands")]
help:
    @just --list --unsorted

[group("Help")]
[doc("Choose a just command interactively")]
choose:
    @if ! command -v fzf >/dev/null 2>&1; then \
        echo "[choose] fzf not installed"; \
        echo "[choose] Install: brew install fzf"; \
        exit 1; \
    elif [ ! -t 0 ] || [ ! -t 1 ]; then \
        echo "[choose] Interactive chooser requires a TTY"; \
        echo "[choose] Run this command from a local interactive terminal"; \
        exit 1; \
    else \
        just --choose; \
    fi
