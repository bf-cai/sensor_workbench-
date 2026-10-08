import { useEffect, useRef, useState } from "react";
import { connectStream, loadMetadata } from "../api/client";
import type { Metadata } from "../api/client";
import type { StreamMessage } from "../api/generated";
import { TimingPlot } from "../components/TimingPlot";

const MAX_POINTS = 300;

/** One live overview driven by HTTP metadata and WebSocket observations. */
export function Overview() {
  const [metadata, setMetadata] = useState<Metadata | null>(null);
  const [error, setError] = useState("");
  const [status, setStatus] = useState("Connecting");
  const [messages, setMessages] = useState<StreamMessage[]>([]);
  const [lastArrival, setLastArrival] = useState<number | null>(null);
  const [now, setNow] = useState(() => performance.now());
  const runId = useRef<string | null>(null);
  useEffect(() => {
    const abort = new AbortController();
    const refresh = () => {
      void loadMetadata(abort.signal)
        .then((data) => {
          setMetadata(data);
          setError("");
        })
        .catch((reason: unknown) => {
          if (!abort.signal.aborted) setError(String(reason));
        });
    };
    refresh();
    const disconnect = connectStream((message) => {
      if (runId.current !== message.run_id) {
        runId.current = message.run_id;
        setMessages([message]);
        refresh();
      } else {
        setMessages((previous) => [...previous, message].slice(-MAX_POINTS));
      }
      setLastArrival(performance.now());
    }, setStatus);
    const ticker = setInterval(() => setNow(performance.now()), 1000);
    return () => {
      abort.abort();
      disconnect();
      clearInterval(ticker);
    };
  }, []);
  const latest = messages.at(-1);
  const observation = latest?.observation;
  const source =
    metadata?.sources.find((item) => item.id === observation?.source_id) ??
    metadata?.sources[0];
  const domainId =
    observation?.raw_timestamp?.clock_domain_id ?? source?.clock_domain_id;
  const domain = metadata?.clocks.find((item) => item.id === domainId);
  const stale = lastArrival !== null && now - lastArrival > 2000;
  const simulated = observation?.simulated ?? source?.simulated;
  return (
    <main>
      <header>
        <div>
          <p className="eyebrow">Local timing diagnostics</p>
          <h1>Sensor Workbench</h1>
        </div>
        <p role="status" className={stale ? "status stale" : "status"}>
          {stale ? "Stale — no recent observations" : status}
        </p>
      </header>
      {error && <p role="alert">{error}</p>}
      <section className="source-panel" aria-label="Source metadata">
        <div>
          <h2>{source?.name ?? "Waiting for source"}</h2>
          <p className="badge">
            {simulated === true
              ? "SIMULATED"
              : simulated === false
                ? "LIVE SOURCE"
                : "Awaiting metadata"}
          </p>
        </div>
        <dl>
          <div>
            <dt>Source</dt>
            <dd>{observation?.source_id ?? source?.id ?? "—"}</dd>
          </div>
          <div>
            <dt>Rate</dt>
            <dd>{source ? `${source.rate_hz} Hz` : "—"}</dd>
          </div>
          <div>
            <dt>Clock domain</dt>
            <dd>{domainId ?? "—"}</dd>
          </div>
          <div>
            <dt>Time scale</dt>
            <dd>{domain?.timescale ?? "—"}</dd>
          </div>
          <div>
            <dt>Epoch</dt>
            <dd>{domain?.epoch_description ?? "—"}</dd>
          </div>
          <div>
            <dt>Provenance</dt>
            <dd>{observation?.provenance ?? source?.provenance ?? "—"}</dd>
          </div>
        </dl>
      </section>
      <section className="chart-panel" aria-label="Live timing observations">
        <div className="chart-heading">
          <h2>{simulated ? "Simulated delay" : "Timing metric"}</h2>
          <p>
            {observation
              ? `${observation.metric.value.toLocaleString()} ${observation.metric.unit}`
              : "Waiting for stream"}
          </p>
        </div>
        <TimingPlot messages={messages} />
        <p className="note">
          Synthetic delay demonstrates the data path. It does not measure clock
          accuracy or physical sensor alignment.
        </p>
        <dl className="stream-details">
          <div>
            <dt>Raw sample time</dt>
            <dd>
              {observation?.raw_timestamp
                ? `${observation.raw_timestamp.value} ${observation.raw_timestamp.unit} (${observation.raw_timestamp.semantics})`
                : "Unavailable"}
            </dd>
          </div>
          <div>
            <dt>Sequence</dt>
            <dd>{observation?.sequence ?? "—"}</dd>
          </div>
          <div>
            <dt>Queue drops since connection</dt>
            <dd>{latest?.dropped_total ?? "—"}</dd>
          </div>
          <div>
            <dt>Process run</dt>
            <dd>{latest?.run_id ?? metadata?.health.run_id ?? "—"}</dd>
          </div>
        </dl>
      </section>
      <footer>
        Last {MAX_POINTS} observations retained in this browser. Sample and host
        receive clocks remain separate.
      </footer>
    </main>
  );
}
