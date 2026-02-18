"""
Client for perfSONAR pScheduler API
"""

import httpx
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


class PSchedulerClient:
    """Client for perfSONAR pScheduler API"""

    def __init__(self, base_url: str):
        """
        Initialize pScheduler client
        
        Args:
            base_url: Base URL for pScheduler API (e.g., https://host/pscheduler)
        """
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(
            timeout=60.0,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
        )

    async def close(self):
        """Close the HTTP client"""
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
        try:
            response = await self.client.post(
                f"{self.base_url}/tasks",
                json=task_request.model_dump(exclude_none=True),
            )
            response.raise_for_status()
            
            data = response.json()
            return PSchedulerTaskResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            raise Exception(
                f"Failed to create task: {e.response.status_code} - {e.response.text}"
            )
        except Exception as e:
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
        try:
            # If it's a relative URL, prepend base_url
            if not task_url.startswith("http"):
                task_url = f"{self.base_url}{task_url}"
            
            response = await self.client.get(task_url)
            response.raise_for_status()
            
            return response.json()
        except httpx.HTTPStatusError as e:
            raise Exception(
                f"Failed to get task info: {e.response.status_code} - {e.response.text}"
            )
        except Exception as e:
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
        try:
            # If it's a relative URL, prepend base_url
            if not run_url.startswith("http"):
                run_url = f"{self.base_url}{run_url}"
            
            response = await self.client.get(run_url)
            response.raise_for_status()
            
            data = response.json()
            return PSchedulerRunStatus.model_validate(data)
        except httpx.HTTPStatusError as e:
            raise Exception(
                f"Failed to get run status: {e.response.status_code} - {e.response.text}"
            )
        except Exception as e:
            raise Exception(f"Failed to get run status: {str(e)}")

    async def get_result(self, run_url: str) -> Optional[PSchedulerResult]:
        """
        Get result of a completed run
        
        Args:
            run_url: Run URL
            
        Returns:
            Test result or None if not available yet
        """
        status = await self.get_run_status(run_url)
        
        if status.state not in ["finished", "failed"]:
            return None
        
        if status.result:
            return PSchedulerResult.model_validate(status.result)
        
        return None

    async def cancel_task(self, task_url: str) -> bool:
        """
        Cancel a task
        
        Args:
            task_url: Task URL
            
        Returns:
            True if successfully cancelled
        """
        try:
            if not task_url.startswith("http"):
                task_url = f"{self.base_url}{task_url}"
            
            response = await self.client.delete(task_url)
            response.raise_for_status()
            
            return True
        except Exception as e:
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
        import asyncio
        
        waited = 0
        while waited < max_wait:
            result = await self.get_result(run_url)
            if result:
                return result
            
            await asyncio.sleep(poll_interval)
            waited += poll_interval
        
        raise TimeoutError(f"Test did not complete within {max_wait} seconds")
