"""
Client for interacting with perfSONAR esmond measurement archive API
"""

import httpx
import logging
from typing import List, Optional, Dict, Any
from .types import (
    PerfSONARConfig,
    MeasurementMetadata,
    MeasurementQueryParams,
    TimeSeriesDataPoint,
    MeasurementDataParams,
    MeasurementResult,
)

logger = logging.getLogger(__name__)


class PerfSONARClient:
    """Client for perfSONAR esmond API"""

    def __init__(self, config: PerfSONARConfig):
        self.base_url = config.base_url or f"http://{config.host}/esmond/perfsonar/archive"
        logger.info(f"Initializing PerfSONARClient with base URL: {self.base_url}")
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30.0,
            headers={"Accept": "application/json"},
        )

    async def close(self):
        """Close the HTTP client"""
        logger.debug("Closing PerfSONARClient HTTP connection")
        await self.client.aclose()

    async def query_measurements(
        self, params: Optional[MeasurementQueryParams] = None
    ) -> List[MeasurementMetadata]:
        """
        Query measurements with optional filters
        
        Args:
            params: Query parameters for filtering measurements
            
        Returns:
            List of measurement metadata
        """
        logger.info("Querying measurements")
        logger.debug(f"Query parameters: {params}")
        try:
            query_params = {}
            if params:
                query_params = params.model_dump(by_alias=True, exclude_none=True)
            
            response = await self.client.get("/", params=query_params)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Retrieved {len(data)} measurement records")
            return [MeasurementMetadata.model_validate(item) for item in data]
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error querying measurements: {e.response.status_code}")
            raise Exception(
                f"Failed to query measurements: {e.response.status_code} - {e.response.text}"
            )
        except Exception as e:
            logger.error(f"Error querying measurements: {str(e)}")
            raise Exception(f"Failed to query measurements: {str(e)}")

    async def get_measurement_data(
        self, params: MeasurementDataParams
    ) -> List[TimeSeriesDataPoint]:
        """
        Get measurement data for a specific event type
        
        Args:
            params: Parameters specifying which measurement data to retrieve
            
        Returns:
            List of time series data points
        """
        logger.info(f"Getting measurement data for event type: {params.event_type}")
        logger.debug(f"Measurement data parameters: {params}")
        try:
            # Build the URL path
            path = f"/{params.metadata_key}/{params.event_type}"
            
            if params.summary_type and params.summary_window:
                path += f"/{params.summary_type}/{params.summary_window}"
            else:
                path += "/base"
            
            logger.debug(f"Request path: {path}")
            
            # Build query params
            query_params: Dict[str, Any] = {}
            if params.time_start:
                query_params["time-start"] = params.time_start
            if params.time_end:
                query_params["time-end"] = params.time_end
            if params.time_range:
                query_params["time-range"] = params.time_range
            
            response = await self.client.get(path, params=query_params)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Retrieved {len(data)} data points")
            return [TimeSeriesDataPoint.model_validate(item) for item in data]
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error getting measurement data: {e.response.status_code}")
            raise Exception(
                f"Failed to get measurement data: {e.response.status_code} - {e.response.text}"
            )
        except Exception as e:
            logger.error(f"Error getting measurement data: {str(e)}")
            raise Exception(f"Failed to get measurement data: {str(e)}")

    async def get_throughput(
        self,
        source: str,
        destination: str,
        time_range: Optional[int] = None,
        summary_window: Optional[int] = None,
    ) -> List[MeasurementResult]:
        """
        Get throughput measurements between source and destination
        
        Args:
            source: Source host/IP address
            destination: Destination host/IP address
            time_range: Time range in seconds from now
            summary_window: Summary window in seconds
            
        Returns:
            List of measurement results
        """
        logger.info(f"Getting throughput: {source} -> {destination}")
        metadata = await self.query_measurements(
            MeasurementQueryParams(
                source=source, destination=destination, event_type="throughput"
            )
        )
        
        results = []
        for meta in metadata:
            event_type = next(
                (e for e in meta.event_types if e.event_type == "throughput"), None
            )
            if not event_type:
                continue
            
            data = await self.get_measurement_data(
                MeasurementDataParams(
                    metadata_key=meta.metadata_key,
                    event_type="throughput",
                    summary_type="averages" if summary_window else None,
                    summary_window=summary_window,
                    time_range=time_range,
                )
            )
            
            results.append(MeasurementResult(metadata=meta, data=data))
        
        logger.info(f"Retrieved {len(results)} throughput results")
        return results

    async def get_latency(
        self,
        source: str,
        destination: str,
        time_range: Optional[int] = None,
        summary_window: Optional[int] = None,
    ) -> List[MeasurementResult]:
        """
        Get latency/delay measurements between source and destination
        
        Args:
            source: Source host/IP address
            destination: Destination host/IP address
            time_range: Time range in seconds from now
            summary_window: Summary window in seconds
            
        Returns:
            List of measurement results
        """
        logger.info(f"Getting latency: {source} -> {destination}")
        # Try histogram-owdelay first, fall back to histogram-rtt
        metadata = await self.query_measurements(
            MeasurementQueryParams(
                source=source, destination=destination, event_type="histogram-owdelay"
            )
        )
        
        if not metadata:
            logger.debug("No histogram-owdelay data, trying histogram-rtt")
            metadata = await self.query_measurements(
                MeasurementQueryParams(
                    source=source, destination=destination, event_type="histogram-rtt"
                )
            )
        
        results = []
        for meta in metadata:
            event_types = ["histogram-owdelay", "histogram-rtt"]
            for event_type_name in event_types:
                event_type = next(
                    (e for e in meta.event_types if e.event_type == event_type_name), None
                )
                if not event_type:
                    continue
                
                data = await self.get_measurement_data(
                    MeasurementDataParams(
                        metadata_key=meta.metadata_key,
                        event_type=event_type_name,
                        summary_type="statistics" if summary_window else None,
                        summary_window=summary_window,
                        time_range=time_range,
                    )
                )
                
                results.append(MeasurementResult(metadata=meta, data=data))
                break
        
        logger.info(f"Retrieved {len(results)} latency results")
        return results

    async def get_packet_loss(
        self,
        source: str,
        destination: str,
        time_range: Optional[int] = None,
        summary_window: Optional[int] = None,
    ) -> List[MeasurementResult]:
        """
        Get packet loss measurements between source and destination
        
        Args:
            source: Source host/IP address
            destination: Destination host/IP address
            time_range: Time range in seconds from now
            summary_window: Summary window in seconds
            
        Returns:
            List of measurement results
        """
        logger.info(f"Getting packet loss: {source} -> {destination}")
        metadata = await self.query_measurements(
            MeasurementQueryParams(
                source=source, destination=destination, event_type="packet-loss-rate"
            )
        )
        
        results = []
        for meta in metadata:
            event_type = next(
                (e for e in meta.event_types if e.event_type == "packet-loss-rate"), None
            )
            if not event_type:
                continue
            
            data = await self.get_measurement_data(
                MeasurementDataParams(
                    metadata_key=meta.metadata_key,
                    event_type="packet-loss-rate",
                    summary_type="aggregations" if summary_window else None,
                    summary_window=summary_window,
                    time_range=time_range,
                )
            )
            
            results.append(MeasurementResult(metadata=meta, data=data))
        
        logger.info(f"Retrieved {len(results)} packet loss results")
        return results

    async def get_available_event_types(
        self, source: Optional[str] = None, destination: Optional[str] = None
    ) -> List[str]:
        """
        Get all available event types for measurements
        
        Args:
            source: Optional source filter
            destination: Optional destination filter
            
        Returns:
            List of event type names
        """
        logger.info("Getting available event types")
        metadata = await self.query_measurements(
            MeasurementQueryParams(source=source, destination=destination)
        )
        
        event_types = set()
        for meta in metadata:
            for event_type in meta.event_types:
                event_types.add(event_type.event_type)
        
        result = sorted(list(event_types))
        logger.info(f"Found {len(result)} event types")
        return result
