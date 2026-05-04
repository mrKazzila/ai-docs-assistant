[group("Stacks")]
[doc("Run qdrant")]
run-qdrant: _docker-ready _qdrant-storage-create
    docker compose up -d qdrant

[group("Stacks")]
[doc("Run indexer")]
run-indexer: _docker-ready
    docker compose up -rm indexer

[group("Stacks")]
[doc("Run API")]
run-api: _docker-ready
    docker compose up -d api


[group("Stacks")]
[doc("Run all stack")]
run-all: run-qdrant run-indexer run-api


[group("Stacks")]
[doc("Stop the Docker stack")]
down-all: _docker-ready
    docker compose down

[group("Stacks")]
[doc("Show Docker stack status")]
ps: _docker-ready
    docker compose ps


[group("Stacks")]
[doc("Restart the Qdrant Docker stack")]
stack-restart: _docker-ready
    docker compose down
    docker compose up -d qdrant

[group("Stacks")]
[doc("Rebuild and restart the API indexer")]
rebuild-indexer-api: _docker-ready
    docker compose build api indexer
    docker compose up -d api indexer

[group("Stacks")]
[doc("Rebuild and restart the full API stack (api + indexer + qdrant)")]
rebuild-all: _docker-ready
    docker compose build --no-cache api indexer
    docker compose up -d qdrant indexer api
