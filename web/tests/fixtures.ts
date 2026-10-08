import type { StreamMessage } from "../src/api/generated";
import type { Metadata } from "../src/api/client";

export const message: StreamMessage = {
  schema_version: 1, run_id: "fixture-run", dropped_total: 2,
  observation: {
    schema_version: 1, event_id: "fixture-run:4", source_id: "fixture-source",
    sequence: 4, kind: "metric", simulated: true, provenance: "Backend test provenance",
    metric: { name: "synthetic_delay", value: 12345, unit: "ns" },
    raw_timestamp: {
      value: "1790000000123456789", unit: "ns", clock_domain_id: "fixture-clock",
      semantics: "sample",
    },
  },
};

export const metadata: Metadata = {
  health: { status: "ok", version: "0.1.0", run_id: "fixture-run" },
  sources: [{
    id: "fixture-source", name: "Backend fixture source", clock_domain_id: "fixture-clock",
    simulated: true, rate_hz: 10, provenance: "Backend test provenance", capabilities: [],
  }],
  clocks: [{
    id: "fixture-clock", owner: "fixture-source", timescale: "DEVICE_LOCAL",
    epoch_description: "Fixture epoch",
  }],
};
