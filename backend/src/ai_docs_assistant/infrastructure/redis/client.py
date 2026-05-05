from redis.asyncio import Redis


def create_redis_client(
    host: str,
    port: int,
    db: int = 0,
    decode_responses: bool = True,
) -> Redis:
    return Redis(
        host=host,
        port=port,
        db=db,
        decode_responses=decode_responses,
    )
