"""
Client for perfSONAR pScheduler API
"""

import json
import logging
from typing import Any, Dict, List, Optional

import httpx

from .types import (
    LatencyTestSpec,
    PSchedulerResult,
    PSchedulerRunStatus,
    PSchedulerTaskRequest,
    PSchedulerTaskResponse,
    PSchedulerTestSpec,
    RTTTestSpec,
    ThroughputTestSpec,
)

logger = logging.getLogger(__name__)


class PSchedulerClient:
    """Client for perfSONAR pScheduler API"""

    def __init__(self, base_url: str):
        """
        Initialize pScheduler client

        Args:
            base_url: Base URL for pScheduler API (e.g., https://host/pscheduler)
        """
        if not base_url:
            raise ValueError("base_url cannot be empty")
        if not base_url.startswith(("http://", "https://")):
            raise ValueError(f"base_url must start with http:// or https://, got: {base_url}")

        self.base_url = base_url.rstrip("/")
        logger.info(f"Initializing PSchedulerClient with base URL: {self.base_url}")
        self.client = httpx.AsyncClient(
            timeout=60.0,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            verify=False,
        )

    async def close(self):
        """Close the HTTP client"""
        logger.debug("Closing PSchedulerClient HTTP connection")
        await self.client.aclose()

    async def create_task(self, task_request: PSchedulerTaskRequest) -> PSchedulerTaskResponse:
        """
        Create a new pScheduler task

        Args:
            task_request: The task request specification

        Returns:
            Task response with task URL
        """
        logger.info(f"Creating pScheduler task of type: {task_request.test.type}")
        logger.debug(f"Task request: {task_request}")
        try:
            url = f"{self.base_url}/tasks"
            payload = task_request.model_dump(exclude_none=True)
            logger.info(f"POST {url}")
            logger.debug(f"Request payload: {json.dumps(payload, indent=2)}")

            response = await self.client.post(url, json=payload)
            logger.debug(f"Response status: {response.status_code}")
            response.raise_for_status()

            data = response.json()
            if isinstance(data, str):
                data = {"task": data}
            result = PSchedulerTaskResponse.model_validate(data)
            logger.info(f"Task created successfully: {result.task}")
            return result
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error creating task: {e.response.status_code}")
            raise Exception(f"Failed to create task: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            logger.error(f"Error creating task: {str(e)}")
            raise Exception(f"Failed to create task: {str(e)}")

    async def schedule_throughput_test(
        self,
        source: Optional[str],
        dest: str,
        duration: str = "PT30S",
        slip: str = "PT10M",
    ) -> PSchedulerTaskResponse:
        """
        Schedule a throughput test

        Args:
            source: Source host (None for local)
            dest: Destination host
            duration: Test duration in ISO 8601 format (e.g., PT30S for 30 seconds)
            slip: Schedule slip time in ISO 8601 format (e.g., PT10M for 10 minutes)

        Returns:
            Task response
        """
        logger.info(
            f"Scheduling throughput test from {source or 'local'} to {dest} with duration {duration}"
        )

        # Determine which node to schedule on (prefer source if available)
        scheduler_node = source or dest
        scheduler_url = f"https://{scheduler_node}/pscheduler"
        logger.info(f"Using pScheduler at: {scheduler_url}")

        test_spec = ThroughputTestSpec(source=source, dest=dest, duration=duration)

        task_request = PSchedulerTaskRequest(
            test=PSchedulerTestSpec(
                type="throughput", spec=test_spec.model_dump(exclude_none=True)
            ),
            schedule={"slip": slip},
        )

        # Create a temporary client for this specific scheduler
        client = PSchedulerClient(scheduler_url)
        try:
            return await client.create_task(task_request)
        finally:
            await client.close()

    async def schedule_latency_test(
        self,
        source: Optional[str],
        dest: str,
        packet_count: int = 600,
        packet_interval: float = 0.1,
        slip: str = "PT10M",
    ) -> PSchedulerTaskResponse:
        """
        Schedule a latency (one-way delay) test

        Args:
            source: Source host (None for local)
            dest: Destination host
            packet_count: Number of packets to send
            packet_interval: Interval between packets in seconds
            slip: Schedule slip time in ISO 8601 format (e.g., PT10M for 10 minutes)

        Returns:
            Task response
        """
        logger.info(
            f"Scheduling latency test from {source or 'local'} to {dest} ({packet_count} packets)"
        )

        # Determine which node to schedule on (prefer source if available)
        scheduler_node = source or dest
        scheduler_url = f"https://{scheduler_node}/pscheduler"
        logger.info(f"Using pScheduler at: {scheduler_url}")

        test_spec = LatencyTestSpec(
            source=source, dest=dest, packet_count=packet_count, packet_interval=packet_interval
        )

        task_request = PSchedulerTaskRequest(
            test=PSchedulerTestSpec(
                type="latency", spec=test_spec.model_dump(by_alias=True, exclude_none=True)
            ),
            schedule={"slip": slip},
        )

        # Create a temporary client for this specific scheduler
        client = PSchedulerClient(scheduler_url)
        try:
            return await client.create_task(task_request)
        finally:
            await client.close()

    async def schedule_rtt_test(
        self, dest: str, count: int = 10, slip: str = "PT10M"
    ) -> PSchedulerTaskResponse:
        """
        Schedule an RTT (round-trip time) test

        Args:
            dest: Destination host
            count: Number of pings
            slip: Schedule slip time in ISO 8601 format (e.g., PT10M for 10 minutes)

        Returns:
            Task response
        """
        logger.info(f"Scheduling RTT test to {dest} ({count} pings)")

        # For RTT tests, schedule on the destination since it measures from local to dest
        scheduler_url = f"https://{dest}/pscheduler"
        logger.info(f"Using pScheduler at: {scheduler_url}")

        test_spec = RTTTestSpec(dest=dest, count=count)

        task_request = PSchedulerTaskRequest(
            test=PSchedulerTestSpec(type="rtt", spec=test_spec.model_dump(exclude_none=True)),
            schedule={"slip": slip},
        )

        # Create a temporary client for this specific scheduler
        client = PSchedulerClient(scheduler_url)
        try:
            return await client.create_task(task_request)
        finally:
            await client.close()

    async def get_task_info(self, task_url: str) -> Dict[str, Any]:
        """
        Get information about a task

        Args:
            task_url: Full URL or path to the task

        Returns:
            Task information
        """
        logger.debug(f"Getting task info: {task_url}")
        try:
            # If it's a relative URL, prepend base_url
            if not task_url.startswith("http"):
                task_url = f"{self.base_url}{task_url}"

            response = await self.client.get(task_url)
            response.raise_for_status()

            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error getting task info: {e.response.status_code}")
            raise Exception(
                f"Failed to get task info: {e.response.status_code} - {e.response.text}"
            )
        except Exception as e:
            logger.error(f"Error getting task info: {str(e)}")
            raise Exception(f"Failed to get task info: {str(e)}")

    async def get_runs(self, task_url: str) -> List[str]:
        """
        Get list of runs for a task

        Args:
            task_url: Task URL

        Returns:
            List of run URLs
        """
        task_info = await self.get_task_info(task_url)
        return task_info.get("detail", {}).get("runs", [])

    async def get_run_status(self, run_url: str) -> PSchedulerRunStatus:
        """
        Get status of a specific run

        Args:
            run_url: Full URL or path to the run

        Returns:
            Run status information
        """
        logger.debug(f"Getting run status: {run_url}")
        try:
            # If it's a relative URL, prepend base_url
            if not run_url.startswith("http"):
                run_url = f"{self.base_url}{run_url}"

            response = await self.client.get(run_url)
            response.raise_for_status()

            data = response.json()
            status = PSchedulerRunStatus.model_validate(data)
            logger.info(f"Run status: {status.state}")
            return status
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error getting run status: {e.response.status_code}")
            raise Exception(
                f"Failed to get run status: {e.response.status_code} - {e.response.text}"
            )
        except Exception as e:
            logger.error(f"Error getting run status: {str(e)}")
            raise Exception(f"Failed to get run status: {str(e)}")

    async def get_result(self, run_url: str) -> Optional[PSchedulerResult]:
        """
        Get result of a completed run

        Args:
            run_url: Run URL

        Returns:
            Test result or None if not available yet
        """
        logger.debug(f"Getting result for run: {run_url}")

        # If a task URL was provided, resolve it to the most recent run
        if "/tasks/" in run_url and "/runs/" not in run_url:
            task_url = run_url
            if not task_url.startswith("http"):
                task_url = f"{self.base_url}{task_url}"
            runs_url = f"{task_url}/runs"
            logger.info(f"Fetching runs list from: {runs_url}")
            response = await self.client.get(runs_url)
            if response.status_code == 404:
                logger.info("No runs found for task yet")
                return None
            response.raise_for_status()
            runs = response.json()
            if isinstance(runs, dict) and "runs" in runs:
                runs = runs.get("runs", [])
            if not runs:
                logger.info("No runs returned for task")
                return None
            # Use the most recent run
            run_url = runs[-1]
            logger.info(f"Using run URL: {run_url}")

        status = await self.get_run_status(run_url)
        logger.info(f"Run status response: {status.model_dump()}")

        if status.state not in ["finished", "failed"]:
            if status.result:
                logger.info("Run state not reported as finished, but result is present")
            else:
                logger.info(f"Run not completed yet, state: {status.state}")
                return None

        if status.result:
            logger.info("Test result available in status")
            return PSchedulerResult.model_validate(status.result)

        # Fallback: try the /result endpoint directly
        result_url = run_url
        if not result_url.startswith("http"):
            result_url = f"{self.base_url}{result_url}"
        if not result_url.endswith("/result"):
            result_url = f"{result_url}/result"

        logger.info(f"Fetching result from: {result_url}")
        try:
            response = await self.client.get(result_url)
            if response.status_code == 404 or response.status_code == 202:
                logger.info("Result not available yet")
                return None
            response.raise_for_status()
            data = response.json()
            logger.info("Test result available from /result endpoint")
            return PSchedulerResult.model_validate(data)
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error getting result: {e.response.status_code}")
            raise Exception(
                f"Failed to get test result: {e.response.status_code} - {e.response.text}"
            )
        except Exception as e:
            logger.error(f"Error getting result: {str(e)}")
            raise Exception(f"Failed to get test result: {str(e)}")

    async def cancel_task(self, task_url: str) -> bool:
        """
        Cancel a task

        Args:
            task_url: Task URL

        Returns:
            True if successfully cancelled
        """
        logger.info(f"Cancelling task: {task_url}")
        try:
            if not task_url.startswith("http"):
                task_url = f"{self.base_url}{task_url}"

            response = await self.client.delete(task_url)
            response.raise_for_status()

            logger.info("Task cancelled successfully")
            return True
        except Exception as e:
            logger.error(f"Error cancelling task: {str(e)}")
            raise Exception(f"Failed to cancel task: {str(e)}")

    async def wait_for_result(
        self, run_url: str, max_wait: int = 300, poll_interval: int = 5
    ) -> PSchedulerResult:
        """
        Wait for a run to complete and return the result

        Args:
            run_url: Run URL
            max_wait: Maximum time to wait in seconds
            poll_interval: How often to check status in seconds

        Returns:
            Test result
        """
        logger.info(
            f"Waiting for test result, max_wait={max_wait}s, poll_interval={poll_interval}s"
        )
        import asyncio

        waited = 0
        while waited < max_wait:
            result = await self.get_result(run_url)
            if result:
                logger.info(f"Test completed after {waited}s")
                return result

            await asyncio.sleep(poll_interval)
            waited += poll_interval

        logger.error(f"Test did not complete within {max_wait}s")
        raise TimeoutError(f"Test did not complete within {max_wait} seconds")
