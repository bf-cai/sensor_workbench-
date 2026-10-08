import { act, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { Overview } from "../src/app/Overview";
import { connectStream, loadMetadata } from "../src/api/client";
import type { StreamMessage } from "../src/api/generated";
import { message, metadata } from "./fixtures";

vi.mock("../src/api/client", () => ({
  connectStream: vi.fn(),
  loadMetadata: vi.fn(),
}));
vi.mock("../src/components/TimingPlot", () => ({
  TimingPlot: ({ messages }: { messages: StreamMessage[] }) => (
    <div data-testid="plot">
      {messages.map((item) => item.observation.metric.value).join(",")}
    </div>
  ),
}));

describe("live overview", () => {
  let onMessage: (message: StreamMessage) => void;
  let onStatus: (status: string) => void;
  const disconnect = vi.fn();
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(loadMetadata).mockResolvedValue(metadata);
    vi.mocked(connectStream).mockImplementation((receiver, status) => {
      onMessage = receiver;
      onStatus = status;
      return disconnect;
    });
  });
  it("renders backend source provenance and received values with exact raw time", async () => {
    const { unmount } = render(<Overview />);
    await screen.findByText("Backend fixture source");
    act(() => {
      onMessage(message);
      onStatus("Connected");
    });
    expect(screen.getByText("SIMULATED")).toBeInTheDocument();
    expect(screen.getByText("Backend test provenance")).toBeInTheDocument();
    expect(screen.getByText("fixture-clock")).toBeInTheDocument();
    expect(
      screen.getByText("1790000000123456789 ns (sample)"),
    ).toBeInTheDocument();
    expect(screen.getByTestId("plot")).toHaveTextContent("12345");
    expect(screen.getByText("2")).toBeInTheDocument();
    unmount();
    expect(disconnect).toHaveBeenCalledOnce();
  });
  it("clears the plot on process restart and bounds retained observations", async () => {
    render(<Overview />);
    await screen.findByText("Backend fixture source");
    act(() => {
      for (let index = 0; index < 310; index++) {
        onMessage({
          ...message,
          observation: {
            ...message.observation,
            sequence: index,
            metric: { ...message.observation.metric, value: index },
          },
        });
      }
    });
    expect(screen.getByTestId("plot").textContent?.split(",")).toHaveLength(
      300,
    );
    act(() => onMessage({ ...message, run_id: "restart" }));
    expect(screen.getByTestId("plot")).toHaveTextContent(/^12345$/);
    await waitFor(() => expect(loadMetadata).toHaveBeenCalledTimes(3));
  });
  it("shows an API error without inventing source metadata", async () => {
    vi.mocked(loadMetadata).mockRejectedValue(new Error("API unavailable"));
    render(<Overview />);
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "API unavailable",
    );
    expect(screen.getByText("Waiting for source")).toBeInTheDocument();
  });
  it("marks observations stale when the stream stops delivering", async () => {
    vi.useFakeTimers();
    try {
      render(<Overview />);
      await act(async () => {
        await Promise.resolve();
      });
      act(() => onMessage(message));
      act(() => {
        vi.advanceTimersByTime(3000);
      });
      expect(screen.getByRole("status")).toHaveTextContent("Stale");
    } finally {
      vi.useRealTimers();
    }
  });
});
