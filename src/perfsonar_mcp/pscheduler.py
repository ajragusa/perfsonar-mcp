"""
Client for perfSONAR pScheduler API
"""

import httpx
import logging
from typing import Optional, Dict, Any, List
from .types import (
    PSchedulerTaskRequest,
    PSchedulerTaskResponse,
    PSchedulerRunStatus,
    PSchedulerResult,
    PSchedulerTestSpec,
    ThroughputTestSpec,
    LatencyTestSpec,
    RTTTestSpec,
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
        self.base_url = base_url.rstrip("/")
        logger.info(f"Initializing PSchedulerClient with base URL: {self.base_url}")
        self.client = httpx.AsyncClient(
            timeout=60.0,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
        )

    async def close(self):
        """Close the HTTP client"""
        logger.debug("Closing PSchedulerClient HTTP connection")
        await self.client.aclose()

    async def create_task(
        self, task_request: PSchedulerTaskRequest
    ) -> PSchedulerTaskResponse:
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
            response = await self.client.post(
                f"{self.base_url}/tasks",
                json=task_request.model_dump(exclude_none=True),
            )
            response.raise_for_status()
            
            data = response.json()
            result = PSchedulerTaskResponse.model_validate(data)
            logger.info(f"Task created successfully: {result.task_url}")
            return result
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error creating task: {e.response.status_code}")
            raise Exception(
                f"Failed to create task: {e.response.status_code} - {e.response.text}"
            )
        except Exception as e:
            logger.error(f"Error creating task: {str(e)}")
            raise Exception(f"Failed to create task: {str(e)}")

    async def schedule_throughput_test(
        self,
        source: Optional[str],
        dest: str,
        duration: str = "PT30S",
    ) -> PSchedulerTaskResponse:
        """
        Schedule a throughput test
        
        Args:
            source: Source host (None for local)
            dest: Destination host
            duration: Test duration in ISO 8601 format (e.g., PT30S for 30 seconds)
            
        Returns:
            Task response
        """
        logger.info(f"Scheduling throughput test to {dest} with duration {duration}")
        test_spec = ThroughputTestSpec(source=source, dest=dest, duration=duration)
        
        task_request = PSchedulerTaskRequest(
            test=PSchedulerTestSpec(
                type="throughput", spec=test_spec.model_dump(exclude_none=True)
            )
        )
        
        return await self.create_task(task_request)

    async def schedule_latency_test(
        self,
        source: Optional[str],
        dest: str,
        packet_count: int = 600,
        packet_interval: float = 0.1,
    ) -> PSchedulerTaskResponse:
        """
        Schedule a latency (one-way delay) test
        
        Args:
            source: Source host (None for local)
            dest: Destination host
            packet_count: Number of packets to send
            packet_interval: Interval between packets in seconds
            
        Returns:
            Task response
        """
        logger.info(f"Scheduling latency test to {dest} ({packet_count} packets)")
        test_spec = LatencyTestSpec(
            source=source, dest=dest, packet_count=packet_count, packet_interval=packet_interval
        )
        
        task_request = PSchedulerTaskRequest(
            test=PSchedulerTestSpec(
                type="latency", spec=test_spec.model_dump(by_alias=True, exclude_none=True)
            )
        )
        
        return await self.create_task(task_request)

    async def schedule_rtt_test(
        self, dest: str, count: int = 10
    ) -> PSchedulerTaskResponse:
        """
        Schedule an RTT (round-trip time) test
        
        Args:
            dest: Destination host
            count: Number of pings
            
        Returns:
            Task response
        """
        logger.info(f"Scheduling RTT test to {dest} ({count} pings)")
        test_spec = RTTTestSpec(dest=dest, count=count)
        
        task_request = PSchedulerTaskRequest(
            test=PSchedulerTestSpec(
                type="rtt", spec=test_spec.model_dump(exclude_none=True)
            )
        )
        
        return await self.create_task(task_request)

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
        status = await self.get_run_status(run_url)
        
        if status.state not in ["finished", "failed"]:
            logger.info(f"Run not completed yet, state: {status.state}")
            return None
        
        if status.result:
            logger.info("Test result available")
            return PSchedulerResult.model_validate(status.result)
        
        logger.info("No result available")
        return None

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
        logger.info(f"Waiting for test result, max_wait={max_wait}s, poll_interval={poll_interval}s")
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
