from typing import Optional

from app.core.config import settings


class RetryDecision:
    def __init__(
        self,
        wait_seconds: int,
        should_retry: bool,
    ) -> None:
        self.wait_seconds = wait_seconds
        self.should_retry = should_retry


def decide_retry(
    retry_after: Optional[int],
    attempt: int,
) -> RetryDecision:
    if retry_after is not None:
        if retry_after > settings.figma_max_retry_wait_seconds:
            return RetryDecision(
                wait_seconds=retry_after,
                should_retry=False,
            )

        return RetryDecision(
            wait_seconds=retry_after,
            should_retry=True,
        )

    wait_seconds = 2 ** attempt

    if wait_seconds > settings.figma_max_retry_wait_seconds:
        return RetryDecision(
            wait_seconds=wait_seconds,
            should_retry=False,
        )

    return RetryDecision(
        wait_seconds=wait_seconds,
        should_retry=True,
    )
