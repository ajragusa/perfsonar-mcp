/**
 * TypeScript types for perfSONAR API
 */

export interface PerfSONARConfig {
  host: string;
  baseUrl?: string;
}

export interface EventType {
  "event-type": string;
  "base-uri": string;
  summaries?: EventSummary[];
  "time-updated"?: number;
}

export interface EventSummary {
  uri: string;
  "summary-type": string;
  "summary-window": number;
  "time-updated"?: number;
}

export interface MeasurementMetadata {
  url: string;
  "metadata-key": string;
  source: string;
  destination: string;
  "measurement-agent": string;
  "input-source": string;
  "input-destination": string;
  "tool-name": string;
  subject_type: string;
  "event-types": EventType[];
  "time-duration"?: number;
  "ip-transport-protocol"?: string;
}

export interface TimeSeriesDataPoint {
  ts: number;
  val: number;
}

export interface MeasurementQueryParams {
  source?: string;
  destination?: string;
  "event-type"?: string;
  "tool-name"?: string;
  "measurement-agent"?: string;
  "time-start"?: number;
  "time-end"?: number;
  "time-range"?: number;
  limit?: number;
}

export interface MeasurementDataParams {
  metadataKey: string;
  eventType: string;
  summaryType?: string;
  summaryWindow?: number;
  timeStart?: number;
  timeEnd?: number;
  timeRange?: number;
}

export interface MeasurementResult {
  metadata: MeasurementMetadata;
  data: TimeSeriesDataPoint[];
}
