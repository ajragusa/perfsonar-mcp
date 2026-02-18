import axios, { AxiosInstance } from "axios";
import type {
  PerfSONARConfig,
  MeasurementMetadata,
  MeasurementQueryParams,
  TimeSeriesDataPoint,
  MeasurementDataParams,
  MeasurementResult,
} from "./types.js";

/**
 * Client for interacting with perfSONAR esmond API
 */
export class PerfSONARClient {
  private client: AxiosInstance;
  private baseUrl: string;

  constructor(config: PerfSONARConfig) {
    this.baseUrl =
      config.baseUrl || `http://${config.host}/esmond/perfsonar/archive`;
    this.client = axios.create({
      baseURL: this.baseUrl,
      timeout: 30000,
      headers: {
        Accept: "application/json",
      },
    });
  }

  /**
   * Query measurements with optional filters
   */
  async queryMeasurements(
    params: MeasurementQueryParams = {}
  ): Promise<MeasurementMetadata[]> {
    try {
      const response = await this.client.get("/", { params });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(
          `Failed to query measurements: ${error.message}${
            error.response?.data ? ` - ${JSON.stringify(error.response.data)}` : ""
          }`
        );
      }
      throw error;
    }
  }

  /**
   * Get measurement data for a specific event type
   */
  async getMeasurementData(
    params: MeasurementDataParams
  ): Promise<TimeSeriesDataPoint[]> {
    try {
      // Build the URL path
      let path = `/${params.metadataKey}/${params.eventType}`;

      if (params.summaryType && params.summaryWindow) {
        path += `/${params.summaryType}/${params.summaryWindow}`;
      } else {
        path += "/base";
      }

      // Build query params
      const queryParams: Record<string, any> = {};
      if (params.timeStart) queryParams["time-start"] = params.timeStart;
      if (params.timeEnd) queryParams["time-end"] = params.timeEnd;
      if (params.timeRange) queryParams["time-range"] = params.timeRange;

      const response = await this.client.get(path, { params: queryParams });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(
          `Failed to get measurement data: ${error.message}${
            error.response?.data ? ` - ${JSON.stringify(error.response.data)}` : ""
          }`
        );
      }
      throw error;
    }
  }

  /**
   * Get throughput measurements between source and destination
   */
  async getThroughput(
    source: string,
    destination: string,
    options: {
      timeRange?: number;
      summaryWindow?: number;
    } = {}
  ): Promise<MeasurementResult[]> {
    const metadata = await this.queryMeasurements({
      source,
      destination,
      "event-type": "throughput",
    });

    const results: MeasurementResult[] = [];
    for (const meta of metadata) {
      const eventType = meta["event-types"].find(
        (e) => e["event-type"] === "throughput"
      );
      if (!eventType) continue;

      const data = await this.getMeasurementData({
        metadataKey: meta["metadata-key"],
        eventType: "throughput",
        summaryType: options.summaryWindow ? "averages" : undefined,
        summaryWindow: options.summaryWindow,
        timeRange: options.timeRange,
      });

      results.push({ metadata: meta, data });
    }

    return results;
  }

  /**
   * Get latency/delay measurements between source and destination
   */
  async getLatency(
    source: string,
    destination: string,
    options: {
      timeRange?: number;
      summaryWindow?: number;
    } = {}
  ): Promise<MeasurementResult[]> {
    // Try histogram-owdelay first, fall back to histogram-rtt
    let metadata = await this.queryMeasurements({
      source,
      destination,
      "event-type": "histogram-owdelay",
    });

    if (metadata.length === 0) {
      metadata = await this.queryMeasurements({
        source,
        destination,
        "event-type": "histogram-rtt",
      });
    }

    const results: MeasurementResult[] = [];
    for (const meta of metadata) {
      const eventTypes = ["histogram-owdelay", "histogram-rtt"];
      for (const eventTypeName of eventTypes) {
        const eventType = meta["event-types"].find(
          (e) => e["event-type"] === eventTypeName
        );
        if (!eventType) continue;

        const data = await this.getMeasurementData({
          metadataKey: meta["metadata-key"],
          eventType: eventTypeName,
          summaryType: options.summaryWindow ? "statistics" : undefined,
          summaryWindow: options.summaryWindow,
          timeRange: options.timeRange,
        });

        results.push({ metadata: meta, data });
        break;
      }
    }

    return results;
  }

  /**
   * Get packet loss measurements between source and destination
   */
  async getPacketLoss(
    source: string,
    destination: string,
    options: {
      timeRange?: number;
      summaryWindow?: number;
    } = {}
  ): Promise<MeasurementResult[]> {
    const metadata = await this.queryMeasurements({
      source,
      destination,
      "event-type": "packet-loss-rate",
    });

    const results: MeasurementResult[] = [];
    for (const meta of metadata) {
      const eventType = meta["event-types"].find(
        (e) => e["event-type"] === "packet-loss-rate"
      );
      if (!eventType) continue;

      const data = await this.getMeasurementData({
        metadataKey: meta["metadata-key"],
        eventType: "packet-loss-rate",
        summaryType: options.summaryWindow ? "aggregations" : undefined,
        summaryWindow: options.summaryWindow,
        timeRange: options.timeRange,
      });

      results.push({ metadata: meta, data });
    }

    return results;
  }

  /**
   * Get all available event types for a measurement
   */
  async getAvailableEventTypes(
    source?: string,
    destination?: string
  ): Promise<string[]> {
    const metadata = await this.queryMeasurements({
      source,
      destination,
    });

    const eventTypes = new Set<string>();
    for (const meta of metadata) {
      for (const eventType of meta["event-types"]) {
        eventTypes.add(eventType["event-type"]);
      }
    }

    return Array.from(eventTypes);
  }
}
