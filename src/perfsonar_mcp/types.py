"""
Type definitions for perfSONAR MCP server
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# Configuration types
class PerfSONARConfig(BaseModel):
    """Configuration for perfSONAR connection"""
    host: str
    base_url: Optional[str] = None


# Measurement Archive types
class EventSummary(BaseModel):
    """Summary information for an event type"""
    uri: str
    summary_type: str = Field(alias="summary-type")
    summary_window: int = Field(alias="summary-window")
    time_updated: Optional[int] = Field(default=None, alias="time-updated")

    class Config:
        populate_by_name = True


class EventType(BaseModel):
    """Event type information"""
    event_type: str = Field(alias="event-type")
    base_uri: str = Field(alias="base-uri")
    summaries: Optional[List[EventSummary]] = None
    time_updated: Optional[int] = Field(default=None, alias="time-updated")

    class Config:
        populate_by_name = True


class MeasurementMetadata(BaseModel):
    """Metadata about a measurement"""
    url: str
    metadata_key: str = Field(alias="metadata-key")
    source: str
    destination: str
    measurement_agent: str = Field(alias="measurement-agent")
    input_source: str = Field(alias="input-source")
    input_destination: str = Field(alias="input-destination")
    tool_name: str = Field(alias="tool-name")
    subject_type: str
    event_types: List[EventType] = Field(alias="event-types")
    time_duration: Optional[int] = Field(default=None, alias="time-duration")
    ip_transport_protocol: Optional[str] = Field(default=None, alias="ip-transport-protocol")

    class Config:
        populate_by_name = True


class TimeSeriesDataPoint(BaseModel):
    """A single time series data point"""
    ts: int  # timestamp
    val: float  # value


class MeasurementQueryParams(BaseModel):
    """Parameters for querying measurements"""
    source: Optional[str] = None
    destination: Optional[str] = None
    event_type: Optional[str] = Field(default=None, alias="event-type")
    tool_name: Optional[str] = Field(default=None, alias="tool-name")
    measurement_agent: Optional[str] = Field(default=None, alias="measurement-agent")
    time_start: Optional[int] = Field(default=None, alias="time-start")
    time_end: Optional[int] = Field(default=None, alias="time-end")
    time_range: Optional[int] = Field(default=None, alias="time-range")
    limit: Optional[int] = None

    class Config:
        populate_by_name = True


class MeasurementDataParams(BaseModel):
    """Parameters for retrieving measurement data"""
    metadata_key: str
    event_type: str
    summary_type: Optional[str] = None
    summary_window: Optional[int] = None
    time_start: Optional[int] = None
    time_end: Optional[int] = None
    time_range: Optional[int] = None


class MeasurementResult(BaseModel):
    """Result containing metadata and data"""
    metadata: MeasurementMetadata
    data: List[TimeSeriesDataPoint]


# Lookup Service types
class LookupServiceRecord(BaseModel):
    """A record from the lookup service"""
    uri: Optional[str] = None
    type: Optional[List[str]] = None
    host_name: Optional[str] = Field(default=None, alias="host-name")
    location_latitude: Optional[float] = Field(default=None, alias="location-latitude")
    location_longitude: Optional[float] = Field(default=None, alias="location-longitude")
    location_city: Optional[str] = Field(default=None, alias="location-city")
    location_country: Optional[str] = Field(default=None, alias="location-country")
    service_type: Optional[List[str]] = Field(default=None, alias="service-type")
    service_locator: Optional[str] = Field(default=None, alias="service-locator")
    access_point: Optional[str] = Field(default=None, alias="access-point")
    administrators: Optional[List[str]] = None
    communities: Optional[List[str]] = None

    class Config:
        populate_by_name = True


class LookupQueryParams(BaseModel):
    """Parameters for lookup service queries"""
    type: Optional[str] = None
    service_type: Optional[str] = None
    host_name: Optional[str] = None
    location_city: Optional[str] = None
    location_country: Optional[str] = None
    community: Optional[str] = None


# pScheduler types
class PSchedulerTestSpec(BaseModel):
    """Test specification for pScheduler"""
    type: str
    spec: Dict[str, Any]


class PSchedulerTaskRequest(BaseModel):
    """Request to create a pScheduler task"""
    test: PSchedulerTestSpec
    schedule: Optional[Dict[str, Any]] = None
    archives: Optional[List[Dict[str, Any]]] = None


class PSchedulerTaskResponse(BaseModel):
    """Response from creating a pScheduler task"""
    task: str  # Task URL
    schedule: Optional[Dict[str, Any]] = None


class PSchedulerRunStatus(BaseModel):
    """Status of a pScheduler run"""
    run: str  # Run URL
    task: str  # Task URL
    state: str  # pending, running, finished, failed, etc.
    state_display: Optional[str] = Field(default=None, alias="state-display")
    start_time: Optional[str] = Field(default=None, alias="start-time")
    end_time: Optional[str] = Field(default=None, alias="end-time")
    result: Optional[Dict[str, Any]] = None

    class Config:
        populate_by_name = True


class PSchedulerResult(BaseModel):
    """Result from a completed pScheduler test"""
    succeeded: bool
    error: Optional[str] = None
    diags: Optional[str] = None
    result: Optional[Dict[str, Any]] = None


class ThroughputTestSpec(BaseModel):
    """Specification for a throughput test"""
    source: Optional[str] = None
    dest: str
    duration: Optional[str] = "PT30S"  # ISO 8601 duration
    interval: Optional[str] = None


class LatencyTestSpec(BaseModel):
    """Specification for a latency test"""
    source: Optional[str] = None
    dest: str
    packet_count: Optional[int] = Field(default=600, alias="packet-count")
    packet_interval: Optional[float] = Field(default=0.1, alias="packet-interval")

    class Config:
        populate_by_name = True


class RTTTestSpec(BaseModel):
    """Specification for an RTT test"""
    dest: str
    count: Optional[int] = 10
    interval: Optional[str] = "PT1S"
