import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_fixed,
)


class HttpProbe:
    def __init__(self, timeout: float = 3.0) -> None:
        self._timeout = timeout

    @retry(
        retry=retry_if_exception_type(
            (
                httpx.ConnectError,
                httpx.ConnectTimeout,
                httpx.ReadTimeout,
                httpx.RemoteProtocolError,
                httpx.HTTPStatusError,
            ),
        ),
        stop=stop_after_attempt(3),
        wait=wait_fixed(0.5),
        reraise=True,
    )
    async def is_available(self, url: str) -> bool:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.get(url)

        if response.status_code >= 500:
            response.raise_for_status()

        return response.status_code == 200
