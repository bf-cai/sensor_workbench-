import { useEffect, useRef } from "react";
import { init } from "echarts/core";
import { LineChart } from "echarts/charts";
import { GridComponent, TooltipComponent } from "echarts/components";
import { SVGRenderer } from "echarts/renderers";
import { use as registerComponents } from "echarts/core";
import type { StreamMessage } from "../api/generated";

registerComponents([LineChart, GridComponent, TooltipComponent, SVGRenderer]);

/** Render bounded backend observations; sample sequence labels avoid epoch math. */
export function TimingPlot({
  messages,
}: {
  messages: readonly StreamMessage[];
}) {
  const container = useRef<HTMLDivElement>(null);
  const chart = useRef<ReturnType<typeof init> | null>(null);
  useEffect(() => {
    if (!container.current) return;
    chart.current = init(container.current, undefined, { renderer: "svg" });
    const resize = () => chart.current?.resize();
    window.addEventListener("resize", resize);
    return () => {
      window.removeEventListener("resize", resize);
      chart.current?.dispose();
      chart.current = null;
    };
  }, []);
  useEffect(() => {
    const unit = messages.at(-1)?.observation.metric.unit ?? "";
    chart.current?.setOption({
      animation: false,
      grid: { left: 80, right: 24, top: 24, bottom: 48 },
      tooltip: { trigger: "axis" },
      xAxis: {
        type: "category",
        name: "Sample sequence",
        nameLocation: "middle",
        nameGap: 30,
        data: messages.map((message) => message.observation.sequence),
      },
      yAxis: { type: "value", name: unit, scale: true },
      series: [
        {
          type: "line",
          showSymbol: false,
          lineStyle: { color: "#2563eb", width: 2 },
          data: messages.map((message) => message.observation.metric.value),
        },
      ],
    });
  }, [messages]);
  return (
    <div
      ref={container}
      className="timing-plot"
      role="img"
      aria-label="Live simulated delay plot"
    />
  );
}
