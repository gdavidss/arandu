import { useEffect, useState } from "react";
import { CardViz } from "./CardViz";

type LinksFile = {
  links: Record<string, string>;
  question_by_name?: Record<string, string>;
  display_by_name?: Record<string, string>;
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

// Public question URL -> the card's public UUID (last path segment).
function publicUuid(url: string): string | null {
  try {
    const seg = new URL(url, window.location.origin).pathname.split("/").filter(Boolean).pop();
    return seg || null;
  } catch {
    return null;
  }
}

type ActiveCard = { uuid: string; title: string; display?: string };

export function App() {
  const [dashboardUrl, setDashboardUrl] = useState("");
  const [questionByName, setQuestionByName] = useState<Record<string, string>>({});
  const [displayByName, setDisplayByName] = useState<Record<string, string>>({});
  const [active, setActive] = useState<ActiveCard | null>(null);
  const [showAbout, setShowAbout] = useState(false);
  const embedUrl = metabaseDashboardUrl(dashboardUrl);

  const REPO = "https://github.com/gdavidss/arandu";

  useEffect(() => {
    fetch("/metabase-dashboards.json", { cache: "no-store" })
      .then((response) => (response.ok ? response.json() : null))
      .then((payload: LinksFile | null) => {
        const links = payload?.links ?? {};
        setDashboardUrl(links.all || Object.values(links)[0] || "");
        setQuestionByName(payload?.question_by_name ?? {});
        setDisplayByName(payload?.display_by_name ?? {});
      })
      .catch(() => setDashboardUrl(""));
  }, []);

  // Esc closes whatever overlay is open.
  useEffect(() => {
    if (!active && !showAbout) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setActive(null);
        setShowAbout(false);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [active, showAbout]);

  // A script injected into the dashboard iframe posts the clicked card's title here.
  // We open our own client-side viewer (no login, no server): it pulls the card's public
  // data and renders it with editable, browser-persisted visualization options.
  useEffect(() => {
    function onMessage(event: MessageEvent) {
      const data = event.data;
      if (!data || data.type !== "fiscallens-card-zoom") return;
      const url = questionByName[data.title];
      const uuid = url ? publicUuid(url) : null;
      if (!uuid) return;
      setActive({ uuid, title: data.title, display: displayByName[data.title] });
    }
    window.addEventListener("message", onMessage);
    return () => window.removeEventListener("message", onMessage);
  }, [questionByName, displayByName]);

  if (!embedUrl) {
    return (
      <main className="graph-only fallback">
        <p>Rode make seed-metabase para gerar o dashboard Metabase.</p>
      </main>
    );
  }

  return (
    <main className="dashboard-page">
      <button
        type="button"
        className="info-btn"
        onClick={() => setShowAbout(true)}
        data-tooltip="Sobre o Arandu"
        aria-label="Sobre o Arandu"
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
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="16" x2="12" y2="12" />
          <line x1="12" y1="8" x2="12.01" y2="8" />
        </svg>
      </button>
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

      {active && (
        <div
          className="zoom-overlay"
          onClick={() => setActive(null)}
          role="dialog"
          aria-modal="true"
        >
          <div className="zoom-modal" onClick={(e) => e.stopPropagation()}>
            <button
              type="button"
              className="zoom-close"
              onClick={() => setActive(null)}
              aria-label="Fechar"
            >
              ✕
            </button>
            <CardViz uuid={active.uuid} title={active.title} display={active.display} />
          </div>
        </div>
      )}

      {showAbout && (
        <div
          className="about-overlay"
          onClick={() => setShowAbout(false)}
          role="dialog"
          aria-modal="true"
        >
          <div className="about-modal" onClick={(e) => e.stopPropagation()}>
            <button
              type="button"
              className="zoom-close"
              onClick={() => setShowAbout(false)}
              aria-label="Fechar"
            >
              ✕
            </button>
            <h1 className="about-title">Arandu</h1>
            <p className="about-sub">Consulta Cívica · uma lente pública para o Brasil</p>

            <p>
              Arandu é uma interface aberta para dados fiscais e econômicos brasileiros. Não
              é partido, campanha, ministério nem jornal — é um instrumento cívico. O objetivo
              não é remover a interpretação; é torná-la auditável.
            </p>
            <p>
              Cada gráfico responde quatro perguntas: de onde vêm os dados, como foram
              transformados, quando foram atualizados e o que observar com cuidado.
            </p>

            <h2 className="about-h2">Como usar</h2>
            <ul className="about-list">
              <li>
                Clique em qualquer gráfico para abri-lo em tela cheia. Você pode trocar o tipo
                de gráfico e dar zoom — suas escolhas ficam salvas no seu navegador.
              </li>
              <li>Use o filtro de período no topo para recortar o tempo.</li>
              <li>Baixe todas as séries em CSV pelo ícone de download.</li>
            </ul>

            <h2 className="about-h2">O projeto</h2>
            <ul className="about-links">
              <li>
                <a href={REPO} target="_blank" rel="noopener noreferrer">
                  Repositório no GitHub ↗
                </a>
              </li>
              <li>
                <a
                  href={`${REPO}/blob/main/metasystemic/CONSTITUTION.md`}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Constituição do projeto ↗
                </a>
              </li>
              <li>
                <a
                  href={`${REPO}/blob/main/CONTRIBUTING.md`}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Como contribuir ↗
                </a>
              </li>
              <li>
                <a
                  href={`${REPO}/blob/main/systemic/data-standard.md`}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Padrão de dados ↗
                </a>
              </li>
            </ul>

            <p className="about-foot">
              Open source. Dados abertos. Método público. Interface calma.
            </p>
          </div>
        </div>
      )}
    </main>
  );
}
