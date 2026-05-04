[group("Stacks")]
[doc("Start the Qdrant Docker stack")]
stack-up: _docker-ready _qdrant-storage-create
    docker compose up -d qdrant

[group("Stacks")]
[doc("Stop the Docker stack")]
stack-down: _docker-ready
    docker compose down

[group("Stacks")]
[doc("Show Docker stack status")]
stack-ps: _docker-ready
    docker compose ps

[group("Stacks")]
[doc("Show recent Qdrant logs")]
stack-logs: _docker-ready
    docker compose logs --tail=100 qdrant

[group("Stacks")]
[doc("Restart the Qdrant Docker stack")]
stack-restart: _docker-ready _qdrant-storage-create
    docker compose down
    docker compose up -d qdrant

[group("Stacks")]
[doc("Start the full API stack in Docker")]
stack-api-up: _docker-ready _qdrant-storage-create _logs-dir-create _docs-dir-check _env-file-check
    docker compose up -d qdrant indexer api

[group("Stacks")]
[doc("Show recent API and indexer logs")]
stack-api-logs: _docker-ready
    docker compose logs --tail=100 api indexer
