set shell := ["bash", "-eu", "-o", "pipefail", "-c"]
export UV_CACHE_DIR := ".uv-cache"

import "helpers.just"
import "convenience.just"
import "stacks.just"
import "quality.just"
