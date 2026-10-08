import type { ClockDomain, Health, Source, StreamMessage } from "./generated";

/** Metadata fetched from the running backend; no embedded source values. */
export interface Metadata {
  health: Health;
  sources: Source[];
  clocks: ClockDomain[];
}

async function getJson<T>(path: string, signal: AbortSignal): Promise<T> {
  const response = await fetch(`/api/v1/${path}`, { signal });
  if (!response.ok) throw new Error(`API ${path}: HTTP ${response.status}`);
  return (await response.json()) as T;
}

/** Read the baseline HTTP contracts with cancellation on unmount. */
export async function loadMetadata(signal: AbortSignal): Promise<Metadata> {
  const [health, sources, clocks] = await Promise.all([
    getJson<Health>("health", signal),
    getJson<Source[]>("sources", signal),
    getJson<ClockDomain[]>("clock-domains", signal),
  ]);
  return { health, sources, clocks };
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

/** Validate chart-facing stream values and reject unsafe timestamp encoding. */
export function parseStreamMessage(text: string): StreamMessage {
  const value: unknown = JSON.parse(text);
  if (!isRecord(value) || !isRecord(value.observation)) {
    throw new Error("Malformed stream message");
  }
  const observation = value.observation;
  const metric = observation.metric;
  const timestamp = observation.raw_timestamp;
  if (
    value.schema_version !== 1 ||
    typeof value.run_id !== "string" ||
    value.run_id.length === 0 ||
    typeof value.dropped_total !== "number" ||
    !Number.isSafeInteger(value.dropped_total) ||
    value.dropped_total < 0 ||
    observation.schema_version !== 1 ||
    typeof observation.source_id !== "string" ||
    typeof observation.event_id !== "string" ||
    typeof observation.sequence !== "number" ||
    !Number.isSafeInteger(observation.sequence) ||
    observation.sequence < 0 ||
    typeof observation.simulated !== "boolean" ||
    typeof observation.provenance !== "string" ||
    !isRecord(metric) ||
    typeof metric.value !== "number" ||
    !Number.isFinite(metric.value) ||
    typeof metric.unit !== "string" ||
    typeof metric.name !== "string" ||
    (timestamp !== null &&
      timestamp !== undefined &&
      (!isRecord(timestamp) ||
        typeof timestamp.value !== "string" ||
        !/^-?[0-9]+$/.test(timestamp.value) ||
        typeof timestamp.clock_domain_id !== "string" ||
        typeof timestamp.unit !== "string" ||
        typeof timestamp.semantics !== "string"))
  ) {
    throw new Error("Unsupported or malformed stream contract");
  }
  return value as unknown as StreamMessage;
}

/** Connect to the same-origin stream; reconnect with bounded backoff.
 * The returned cleanup function closes the socket and cancels retries.
 * Process run IDs are carried in messages so callers can detect clock resets.
 */
export function connectStream(
  onMessage: (message: StreamMessage) => void,
  onStatus: (status: string) => void,
): () => void {
  let disposed = false;
  let timer: ReturnType<typeof setTimeout> | undefined;
  let socket: WebSocket | undefined;
  let delay = 500;
  function connect(): void {
    if (disposed) return;
    onStatus("Connecting");
    const protocol = location.protocol === "https:" ? "wss:" : "ws:";
    socket = new WebSocket(`${protocol}//${location.host}/api/v1/stream`);
    socket.onopen = () => {
      delay = 500;
      onStatus("Connected");
    };
    socket.onmessage = (event: MessageEvent<unknown>) => {
      try {
        if (typeof event.data !== "string")
          throw new Error("Expected JSON text");
        onMessage(parseStreamMessage(event.data));
        onStatus("Connected");
      } catch {
        onStatus("Invalid stream data");
      }
    };
    socket.onerror = () => onStatus("Stream error");
    socket.onclose = () => {
      if (!disposed) {
        onStatus("Reconnecting");
        timer = setTimeout(connect, delay);
        delay = Math.min(delay * 2, 10_000);
      }
    };
  }
  connect();
  return () => {
    disposed = true;
    clearTimeout(timer);
    if (socket) {
      socket.onopen = null;
      socket.onmessage = null;
      socket.onerror = null;
      socket.onclose = null;
      socket.close();
    }
  };
}
