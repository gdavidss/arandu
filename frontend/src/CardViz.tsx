import { useEffect, useMemo, useRef, useState } from "react";
import * as echarts from "echarts";

// Client-side, login-free card viewer. It pulls the card's data from Metabase's PUBLIC
// query API and renders it ourselves, so the user can change the visualization (type,
// log axis, zoom) with everything persisted in their own browser (localStorage). Nothing
// is written back to Metabase or the server.

type Col = { name: string; base_type?: string };
type Row = Array<string | number | null>;
type ChartType = "line" | "bar" | "area" | "scatter" | "pie";

// Calm, neutral categorical palette (the brand green is chrome only, never data).
const PALETTE = [
  "#3b6fb0", "#e0843b", "#4f9d69", "#9a6fb0",
  "#c1553b", "#5aa6a6", "#b8902f", "#7d7d7d",
];

const NUM = /Integer|Decimal|Float|Number|BigInteger|Currency/i;
const DATE = /Date|Time|Instant/i;
const TEXT = /Text|Category|Name/i;

type Norm = {
  mode: "time" | "category";
  categories: string[];
  series: { name: string; data: unknown[] }[];
  hasNonPositive: boolean;
};

function normalize(cols: Col[], rows: Row[]): Norm {
  const dateIdx = cols.findIndex((c) => DATE.test(c.base_type || ""));
  const textIdxs = cols
    .map((c, i) => [c, i] as const)
    .filter(([c]) => TEXT.test(c.base_type || ""))
    .map(([, i]) => i);
  const numIdxs = cols
    .map((c, i) => [c, i] as const)
    .filter(([c]) => NUM.test(c.base_type || ""))
    .map(([, i]) => i);
  const xIdx = dateIdx >= 0 ? dateIdx : textIdxs[0] ?? 0;
  const mode: "time" | "category" = dateIdx >= 0 ? "time" : "category";
  const dimIdx = textIdxs.find((i) => i !== xIdx);

  const categories: string[] = [];
  let series: { name: string; data: unknown[] }[] = [];
  let hasNonPositive = false;
  const note = (v: unknown) => {
    if (typeof v === "number" && v <= 0) hasNonPositive = true;
  };

  if (mode === "time") {
    if (dimIdx != null && numIdxs.length >= 1) {
      const valIdx = numIdxs[0];
      const m = new Map<string, unknown[]>();
      for (const r of rows) {
        const k = String(r[dimIdx] ?? "—");
        if (!m.has(k)) m.set(k, []);
        const y = r[valIdx] as number;
        note(y);
        m.get(k)!.push([new Date(String(r[xIdx])).getTime(), y]);
      }
      series = [...m.entries()].map(([name, data]) => ({ name, data }));
    } else {
      series = numIdxs.map((i) => ({
        name: cols[i].name,
        data: rows.map((r) => {
          const y = r[i] as number;
          note(y);
          return [new Date(String(r[xIdx])).getTime(), y];
        }),
      }));
    }
  } else {
    const seen = new Set<string>();
    for (const r of rows) {
      const c = String(r[xIdx]);
      if (!seen.has(c)) {
        seen.add(c);
        categories.push(c);
      }
    }
    if (dimIdx != null && numIdxs.length >= 1) {
      const valIdx = numIdxs[0];
      const m = new Map<string, Map<string, number>>();
      for (const r of rows) {
        const k = String(r[dimIdx] ?? "—");
        if (!m.has(k)) m.set(k, new Map());
        const y = r[valIdx] as number;
        note(y);
        m.get(k)!.set(String(r[xIdx]), y);
      }
      series = [...m.entries()].map(([name, cm]) => ({
        name,
        data: categories.map((c) => cm.get(c) ?? null),
      }));
    } else {
      series = numIdxs.map((i) => {
        const cm = new Map<string, number>(rows.map((r) => [String(r[xIdx]), r[i] as number]));
        return {
          name: cols[i].name,
          data: categories.map((c) => {
            const y = cm.get(c) ?? null;
            note(y);
            return y;
          }),
        };
      });
    }
  }
  return { mode, categories, series, hasNonPositive };
}

function mapDefault(display?: string): ChartType {
  switch (display) {
    case "bar":
    case "row":
      return "bar";
    case "area":
      return "area";
    case "pie":
      return "pie";
    case "scatter":
      return "scatter";
    default:
      return "line";
  }
}

function buildOption(n: Norm, type: ChartType, log: boolean): echarts.EChartsOption {
  if (type === "pie") {
    const s = n.series[0];
    const data =
      n.mode === "category"
        ? n.categories.map((c, i) => ({ name: c, value: (s?.data[i] as number) ?? 0 }))
        : ((s?.data ?? []) as Array<[number, number]>).map((p) => ({
            name: new Date(p[0]).toLocaleDateString("pt-BR"),
            value: p[1],
          }));
    return {
      color: PALETTE,
      tooltip: { trigger: "item" },
      legend: { type: "scroll", bottom: 0, textStyle: { color: "#374151" } },
      series: [{ type: "pie", radius: ["42%", "70%"], data, label: { color: "#374151" } }],
    };
  }
  const etype = type === "area" || type === "line" ? "line" : type === "scatter" ? "scatter" : "bar";
  const area = type === "area" ? { areaStyle: { opacity: 0.15 } } : {};
  const multi = n.series.length > 1;
  const xAxis =
    n.mode === "time"
      ? { type: "time" as const, axisLabel: { color: "#6b7280" } }
      : {
          type: "category" as const,
          data: n.categories,
          axisLabel: { color: "#6b7280", interval: 0, rotate: n.categories.length > 6 ? 30 : 0 },
        };
  return {
    color: PALETTE,
    tooltip: { trigger: etype === "scatter" ? "item" : "axis" },
    legend: multi ? { type: "scroll", top: 0, textStyle: { color: "#374151" } } : undefined,
    grid: { left: 60, right: 24, top: multi ? 36 : 16, bottom: 70, containLabel: true },
    xAxis,
    yAxis: {
      type: log ? "log" : "value",
      scale: true,
      axisLabel: { color: "#6b7280" },
      splitLine: { lineStyle: { color: "#eee" } },
    },
    dataZoom: [{ type: "inside" }, { type: "slider", height: 18, bottom: 32 }],
    series: n.series.map((s) => ({
      name: s.name,
      type: etype,
      ...area,
      showSymbol: false,
      smooth: false,
      emphasis: { focus: "series" },
      data: s.data,
    })) as echarts.EChartsOption["series"],
  };
}

const TYPES: { id: ChartType; label: string }[] = [
  { id: "line", label: "Linha" },
  { id: "bar", label: "Barra" },
  { id: "area", label: "Área" },
  { id: "scatter", label: "Pontos" },
  { id: "pie", label: "Pizza" },
];

export function CardViz({ uuid, title, display }: { uuid: string; title: string; display?: string }) {
  const key = `arandu:viz:${uuid}`;
  const saved = useMemo<{ type?: ChartType; log?: boolean } | null>(() => {
    try {
      return JSON.parse(localStorage.getItem(key) || "null");
    } catch {
      return null;
    }
  }, [key]);
  const [type, setType] = useState<ChartType>(saved?.type ?? mapDefault(display));
  const [log, setLog] = useState<boolean>(saved?.log ?? false);
  const [norm, setNorm] = useState<Norm | null>(null);
  const [error, setError] = useState<string | null>(null);
  const elRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    let alive = true;
    setNorm(null);
    setError(null);
    fetch(`/metabase/api/public/card/${uuid}/query`, { cache: "no-store" })
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(String(r.status)))))
      .then((d) => {
        if (!alive) return;
        const data = d?.data ?? {};
        setNorm(normalize(data.cols ?? [], data.rows ?? []));
      })
      .catch((e) => alive && setError(String(e)));
    return () => {
      alive = false;
    };
  }, [uuid]);

  useEffect(() => {
    localStorage.setItem(key, JSON.stringify({ type, log }));
  }, [key, type, log]);

  useEffect(() => {
    if (!elRef.current) return;
    const chart = echarts.init(elRef.current);
    chartRef.current = chart;
    const ro = new ResizeObserver(() => chart.resize());
    ro.observe(elRef.current);
    return () => {
      ro.disconnect();
      chart.dispose();
      chartRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (!chartRef.current || !norm) return;
    chartRef.current.setOption(buildOption(norm, type, log), true);
  }, [norm, type, log]);

  const singleSeries = !!norm && norm.series.length === 1;
  const canLog = !norm || !norm.hasNonPositive;

  return (
    <div className="viz-wrap">
      <div className="viz-toolbar">
        <span className="viz-title">{title}</span>
        <span className="viz-spacer" />
        {TYPES.filter((t) => t.id !== "pie" || singleSeries).map((t) => (
          <button
            key={t.id}
            type="button"
            className={"viz-btn" + (type === t.id ? " is-active" : "")}
            onClick={() => setType(t.id)}
          >
            {t.label}
          </button>
        ))}
        <button
          type="button"
          className={"viz-btn" + (log ? " is-active" : "")}
          disabled={!canLog}
          onClick={() => setLog((v) => !v)}
          title={canLog ? "Escala logarítmica" : "Indisponível (há valores ≤ 0)"}
        >
          log
        </button>
        <button
          type="button"
          className="viz-btn"
          onClick={() => {
            localStorage.removeItem(key);
            setType(mapDefault(display));
            setLog(false);
          }}
          title="Restaurar padrão"
        >
          ↺
        </button>
      </div>
      {error ? (
        <div className="viz-msg">Não foi possível carregar os dados ({error}).</div>
      ) : !norm ? (
        <div className="viz-msg">Carregando…</div>
      ) : null}
      <div
        className="viz-chart"
        ref={elRef}
        style={{ visibility: norm && !error ? "visible" : "hidden" }}
      />
    </div>
  );
}
