compose := "docker compose"

[group("Internal")]
[private]
[doc("Build application images")]
_build: _stack-ready
    {{compose}} build api indexer

[group("Internal")]
[private]
[doc("Build the indexer image")]
_build-indexer: _stack-ready
    {{compose}} build indexer

[group("Internal")]
[private]
[doc("Build the API image")]
_build-api: _api-ready
    {{compose}} build api

[group("Stacks")]
[doc("Run qdrant")]
run-qdrant: _stack-ready
    {{compose}} up -d qdrant

[group("Stacks")]
[doc("Run indexer")]
run-indexer: _build-indexer _indexer-service-clean
    {{compose}} up -d qdrant
    {{compose}} run --rm --no-deps indexer

[group("Stacks")]
[doc("Run API")]
run-api: _build-api
    {{compose}} up -d api

[group("Stacks")]
[doc("Run all stack")]
run-all: _build _indexer-service-clean
    {{compose}} up -d qdrant
    {{compose}} run --rm --no-deps indexer
    {{compose}} up -d api

[group("Stacks")]
[doc("Stop the Docker stack")]
down-all: _docker-ready
    {{compose}} down

[group("Stacks")]
[doc("Show Docker stack status")]
ps: _docker-ready
    {{compose}} ps

[group("Stacks")]
[doc("Restart the full Docker stack")]
stack-restart: _build
    {{compose}} down
    {{compose}} rm -fsv indexer >/dev/null 2>&1 || true
    {{compose}} up -d qdrant
    {{compose}} run --rm --no-deps indexer
    {{compose}} up -d api

[group("Stacks")]
[doc("Rebuild and restart the API and indexer workflow")]
rebuild-indexer-api: _api-ready _indexer-service-clean
    {{compose}} build --no-cache api indexer
    {{compose}} up -d qdrant
    {{compose}} run --rm --no-deps indexer
    {{compose}} up -d api

[group("Stacks")]
[doc("Rebuild and restart the full API stack (api + indexer + qdrant)")]
rebuild-all: _api-ready _indexer-service-clean
    {{compose}} build --no-cache api indexer
    {{compose}} down
    {{compose}} rm -fsv indexer >/dev/null 2>&1 || true
    {{compose}} up -d qdrant
    {{compose}} run --rm --no-deps indexer
    {{compose}} up -d api
