import { afterEach, describe, expect, it, vi } from "vitest";
import { connectStream, parseStreamMessage } from "../src/api/client";
import { message } from "./fixtures";

class SocketFixture {
  static instances: SocketFixture[] = [];
  onopen: (() => void) | null = null;
  onclose: (() => void) | null = null;
  onerror: (() => void) | null = null;
  onmessage: ((event: MessageEvent<unknown>) => void) | null = null;
  close = vi.fn();
  constructor(public url: string) { SocketFixture.instances.push(this); }
}

afterEach(() => { vi.unstubAllGlobals(); vi.useRealTimers(); SocketFixture.instances = []; });

describe("stream contract", () => {
  it("preserves integer strings without epoch rounding", () => {
    expect(parseStreamMessage(JSON.stringify(message)).observation.raw_timestamp?.value)
      .toBe("1790000000123456789");
  });
  it.each(["{}", "not json", JSON.stringify({ ...message, dropped_total: -1 }),
    JSON.stringify({ ...message, schema_version: 2 }),
    JSON.stringify({ ...message, observation: { ...message.observation, metric: { value: "bad" } } }),
    JSON.stringify({ ...message, observation: { ...message.observation,
      raw_timestamp: { value: 1790000000123456789 } } }),
  ])("rejects malformed or unsupported input: %s", (text) => {
    expect(() => parseStreamMessage(text)).toThrow();
  });
  it("reconnects and cancels retries on cleanup", () => {
    vi.useFakeTimers();
    vi.stubGlobal("WebSocket", SocketFixture);
    const receiver = vi.fn();
    const status = vi.fn();
    const stop = connectStream(receiver, status);
    const first = SocketFixture.instances[0];
    expect(first?.url).toContain("/api/v1/stream");
    first?.onopen?.();
    first?.onmessage?.(new MessageEvent("message", { data: JSON.stringify(message) }));
    expect(receiver).toHaveBeenCalledWith(message);
    first?.onclose?.();
    expect(status).toHaveBeenLastCalledWith("Reconnecting");
    vi.advanceTimersByTime(500);
    expect(SocketFixture.instances).toHaveLength(2);
    SocketFixture.instances[1]?.onclose?.();
    stop();
    vi.advanceTimersByTime(10000);
    expect(SocketFixture.instances).toHaveLength(2);
    expect(SocketFixture.instances[1]?.close).toHaveBeenCalledOnce();
  });
});
