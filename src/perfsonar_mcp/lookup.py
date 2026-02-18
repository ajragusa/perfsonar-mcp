"""
Client for perfSONAR Lookup Service (sLS)
"""

import httpx
import logging
from typing import List, Optional, Dict, Any
from .types import LookupServiceRecord, LookupQueryParams

logger = logging.getLogger(__name__)


class LookupServiceClient:
    """Client for perfSONAR Simple Lookup Service (sLS)"""

    def __init__(self, base_url: str = "https://lookup.perfsonar.net/lookup"):
        self.base_url = base_url
        logger.info(f"Initializing LookupServiceClient with base URL: {self.base_url}")
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={"Accept": "application/json"},
        )

    async def close(self):
        """Close the HTTP client"""
        logger.debug("Closing LookupServiceClient HTTP connection")
        await self.client.aclose()

    async def search_records(
        self, params: Optional[LookupQueryParams] = None
    ) -> List[LookupServiceRecord]:
        """
        Search for records in the lookup service
        
        Args:
            params: Query parameters for filtering records
            
        Returns:
            List of lookup service records
        """
        logger.info("Searching lookup service records")
        logger.debug(f"Search parameters: {params}")
        try:
            query_params = {}
            if params:
                query_params = params.model_dump(exclude_none=True)
            
            response = await self.client.get(
                f"{self.base_url}/records", params=query_params
            )
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Found {len(data)} lookup service records")
            return [LookupServiceRecord.model_validate(item) for item in data]
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error searching lookup service: {e.response.status_code}")
            raise Exception(
                f"Failed to search lookup service: {e.response.status_code} - {e.response.text}"
            )
        except Exception as e:
            logger.error(f"Error searching lookup service: {str(e)}")
            raise Exception(f"Failed to search lookup service: {str(e)}")

    async def find_testpoints(
        self,
        service_type: Optional[str] = None,
        location_city: Optional[str] = None,
        location_country: Optional[str] = None,
    ) -> List[LookupServiceRecord]:
        """
        Find perfSONAR testpoints/measurement archives
        
        Args:
            service_type: Filter by service type (e.g., 'ps:MeasurementArchive')
            location_city: Filter by city
            location_country: Filter by country
            
        Returns:
            List of testpoint records
        """
        logger.info(f"Finding testpoints (city={location_city}, country={location_country})")
        params = LookupQueryParams(
            type="service",
            service_type=service_type or "ps:MeasurementArchive",
            location_city=location_city,
            location_country=location_country,
        )
        return await self.search_records(params)

    async def find_hosts(
        self,
        host_name: Optional[str] = None,
        location_city: Optional[str] = None,
        location_country: Optional[str] = None,
    ) -> List[LookupServiceRecord]:
        """
        Find perfSONAR hosts
        
        Args:
            host_name: Filter by hostname
            location_city: Filter by city
            location_country: Filter by country
            
        Returns:
            List of host records
        """
        logger.info(f"Finding hosts (name={host_name}, city={location_city}, country={location_country})")
        params = LookupQueryParams(
            type="host",
            host_name=host_name,
            location_city=location_city,
            location_country=location_country,
        )
        return await self.search_records(params)

    async def find_pscheduler_services(
        self,
        location_city: Optional[str] = None,
        location_country: Optional[str] = None,
    ) -> List[LookupServiceRecord]:
        """
        Find pScheduler services for running tests
        
        Args:
            location_city: Filter by city
            location_country: Filter by country
            
        Returns:
            List of pScheduler service records
        """
        logger.info(f"Finding pScheduler services (city={location_city}, country={location_country})")
        params = LookupQueryParams(
            type="service",
            service_type="pscheduler",
            location_city=location_city,
            location_country=location_country,
        )
        return await self.search_records(params)

    async def get_host_details(self, host_name: str) -> Optional[LookupServiceRecord]:
        """
        Get detailed information about a specific host
        
        Args:
            host_name: The hostname to look up
            
        Returns:
            Host record or None if not found
        """
        logger.info(f"Getting host details for: {host_name}")
        records = await self.find_hosts(host_name=host_name)
        if records:
            logger.info(f"Found host: {host_name}")
        else:
            logger.info(f"Host not found: {host_name}")
        return records[0] if records else None
