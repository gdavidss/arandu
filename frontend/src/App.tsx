import { useEffect, useState } from "react";

type LinksFile = {
  links: Record<string, string>;
  question_by_name?: Record<string, string>;
  question_edit_by_name?: Record<string, string>;
};

function metabaseDashboardUrl(url: string) {
  if (!url) {
    return "";
  }

  const [rawBase, hash = ""] = url.split("#");
  const parsed = new URL(rawBase, window.location.origin);
  const params = new URLSearchParams(hash);
  params.set("titled", "false");
  params.set("bordered", "false");
  params.set("background", "false");
  return `/metabase${parsed.pathname}${parsed.search}#${params.toString()}`;
}

// Public question URL -> same-origin proxied embed URL, with chrome stripped.
function metabaseQuestionUrl(url: string) {
  const parsed = new URL(url, window.location.origin);
  return `/metabase${parsed.pathname}${parsed.search}#titled=false&bordered=false`;
}

// Interactive (logged-in) question URL -> same-origin proxied URL. This is the full
// Metabase question view, where the user can change the visualization and use native
// chart interactions (requires being logged into Metabase once).
function metabaseInteractiveUrl(url: string) {
  const parsed = new URL(url, window.location.origin);
  return `/metabase${parsed.pathname}${parsed.search}`;
}

export function App() {
  const [dashboardUrl, setDashboardUrl] = useState("");
  const [questionByName, setQuestionByName] = useState<Record<string, string>>({});
  const [questionEditByName, setQuestionEditByName] = useState<Record<string, string>>({});
  const [zoomUrl, setZoomUrl] = useState<string | null>(null);
  const embedUrl = metabaseDashboardUrl(dashboardUrl);

  useEffect(() => {
    fetch("/metabase-dashboards.json", { cache: "no-store" })
      .then((response) => (response.ok ? response.json() : null))
      .then((payload: LinksFile | null) => {
        const links = payload?.links ?? {};
        setDashboardUrl(links.all || Object.values(links)[0] || "");
        setQuestionByName(payload?.question_by_name ?? {});
        setQuestionEditByName(payload?.question_edit_by_name ?? {});
      })
      .catch(() => setDashboardUrl(""));
  }, []);

  // Esc closes the zoom modal.
  useEffect(() => {
    if (!zoomUrl) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setZoomUrl(null);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [zoomUrl]);

  // A script injected into the dashboard iframe posts the clicked card's title here.
  // We open that card's full Metabase question view full-screen, where the user can change
  // the visualization (chart type, axes/zoom, settings) and use native interactions. Falls
  // back to the read-only public embed if the interactive URL isn't available.
  useEffect(() => {
    function onMessage(event: MessageEvent) {
      const data = event.data;
      if (!data || data.type !== "fiscallens-card-zoom") return;
      const editUrl = questionEditByName[data.title];
      if (editUrl) {
        setZoomUrl(metabaseInteractiveUrl(editUrl));
        return;
      }
      const url = questionByName[data.title];
      if (url) setZoomUrl(metabaseQuestionUrl(url));
    }
    window.addEventListener("message", onMessage);
    return () => window.removeEventListener("message", onMessage);
  }, [questionByName, questionEditByName]);

  if (!embedUrl) {
    return (
      <main className="graph-only fallback">
        <p>Rode make seed-metabase para gerar o dashboard Metabase.</p>
      </main>
    );
  }

  return (
    <main className="dashboard-page">
      <a
        className="download-btn"
        href="/arandu-data.csv"
        download="arandu-data.csv"
        data-tooltip="Baixar todos os dados (todas as séries, CSV)"
        aria-label="Baixar todos os dados (todas as séries, CSV)"
      >
        <svg
          width="18"
          height="18"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
          <polyline points="7 10 12 15 17 10" />
          <line x1="12" y1="15" x2="12" y2="3" />
        </svg>
      </a>
      <iframe
        className="metabase-dashboard"
        src={embedUrl}
        title="Indicadores macrofiscais do Brasil"
      />

      {zoomUrl && (
        <div
          className="zoom-overlay"
          onClick={() => setZoomUrl(null)}
          role="dialog"
          aria-modal="true"
        >
          <div className="zoom-modal" onClick={(e) => e.stopPropagation()}>
            <button
              type="button"
              className="zoom-close"
              onClick={() => setZoomUrl(null)}
              aria-label="Fechar"
            >
              ✕
            </button>
            <div className="zoom-hint">
              Mude o tipo de gráfico, ajuste eixos e dê zoom aqui. Se aparecer a tela de login,
              entre no Metabase uma vez para liberar a edição.
            </div>
            <iframe className="zoom-frame" src={zoomUrl} title="Gráfico em tela cheia" />
          </div>
        </div>
      )}
    </main>
  );
}
