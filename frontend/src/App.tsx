import { useEffect, useState } from "react";

type LinksFile = {
  links: Record<string, string>;
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

// Full Metabase question URL -> same-origin proxied path (the proxy carries the session,
// so this opens the real, editable question — no login wall).
function proxiedQuestion(url: string) {
  const parsed = new URL(url, window.location.origin);
  return `/metabase${parsed.pathname}${parsed.search}`;
}

// /question/<id> -> "<id>" (used as the localStorage key for the saved visualization).
function cardId(url: string): string | null {
  try {
    return new URL(url, window.location.origin).pathname.split("/").filter(Boolean).pop() || null;
  } catch {
    return null;
  }
}

type Zoom = { src: string; title: string };

export function App() {
  const [dashboardUrl, setDashboardUrl] = useState("");
  const [questionEditByName, setQuestionEditByName] = useState<Record<string, string>>({});
  const [showAbout, setShowAbout] = useState(false);
  const [showMcp, setShowMcp] = useState(false);
  const [zoom, setZoom] = useState<Zoom | null>(null);
  const embedUrl = metabaseDashboardUrl(dashboardUrl);

  const REPO = "https://github.com/gdavidss/arandu";
  const MCP_URL = "http://localhost:8808/mcp";

  useEffect(() => {
    fetch("/metabase-dashboards.json", { cache: "no-store" })
      .then((response) => (response.ok ? response.json() : null))
      .then((payload: LinksFile | null) => {
        const links = payload?.links ?? {};
        setDashboardUrl(links.all || Object.values(links)[0] || "");
        setQuestionEditByName(payload?.question_edit_by_name ?? {});
      })
      .catch(() => setDashboardUrl(""));
  }, []);

  // Esc closes whatever overlay is open (card zoom, About, MCP).
  useEffect(() => {
    if (!zoom && !showAbout && !showMcp) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key !== "Escape") return;
      if (zoom) setZoom(null);
      else if (showMcp) setShowMcp(false);
      else setShowAbout(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [zoom, showAbout, showMcp]);

  // A script injected into the dashboard iframe posts the clicked card's title here.
  // We open the card's real Metabase question (the native visualization editor — table,
  // pie, bar, settings, everything) in a MODAL: an <iframe> over the dashboard. OSS
  // Metabase normally blocks the full app inside iframes (EE-only "interactive
  // embedding"), so the proxy patches out its `window.self !== window.top` self-check
  // and the app boots framed. The user's visualization is persisted per card to
  // localStorage by the proxy-injected script; we restore it here.
  useEffect(() => {
    function onMessage(event: MessageEvent) {
      const data = event.data;
      if (!data || data.type !== "fiscallens-card-zoom") return;
      const editUrl = questionEditByName[data.title];
      const id = editUrl ? cardId(editUrl) : null;
      if (!editUrl || !id) return;
      const saved = localStorage.getItem(`arandu:viz2:${id}`);
      const valid = saved && saved.startsWith("/metabase/") && saved.includes("/question");
      setZoom({ src: valid ? (saved as string) : proxiedQuestion(editUrl), title: data.title });
    }
    window.addEventListener("message", onMessage);
    return () => window.removeEventListener("message", onMessage);
  }, [questionEditByName]);

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
      <button
        type="button"
        className="mcp-btn"
        onClick={() => setShowMcp(true)}
        data-tooltip="Conectar um agente (MCP)"
        aria-label="Conectar um agente (MCP)"
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
          <path d="M9 2v6" />
          <path d="M15 2v6" />
          <path d="M6 8h12v3a6 6 0 0 1-12 0V8Z" />
          <path d="M12 17v5" />
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

      {zoom && (
        <div
          className="zoom-overlay"
          onClick={() => setZoom(null)}
          role="dialog"
          aria-modal="true"
          aria-label={zoom.title}
        >
          <div className="zoom-modal" onClick={(e) => e.stopPropagation()}>
            <button
              type="button"
              className="zoom-close"
              onClick={() => setZoom(null)}
              aria-label="Fechar"
            >
              ✕
            </button>
            <iframe className="zoom-frame" src={zoom.src} title={zoom.title} />
          </div>
        </div>
      )}

      {showMcp && (
        <div
          className="about-overlay"
          onClick={() => setShowMcp(false)}
          role="dialog"
          aria-modal="true"
        >
          <div className="about-modal" onClick={(e) => e.stopPropagation()}>
            <button
              type="button"
              className="zoom-close"
              onClick={() => setShowMcp(false)}
              aria-label="Fechar"
            >
              ✕
            </button>
            <h1 className="about-title">Conecte um agente</h1>
            <p className="about-sub">Os mesmos dados dos gráficos, via MCP</p>

            <p>
              O Arandu expõe um servidor <strong>MCP</strong> (Model Context Protocol): qualquer
              agente — Claude Code, Claude Desktop, Cursor — pode ler as mesmas séries que os
              gráficos mostram, com a mesma proveniência. O acesso é somente leitura.
            </p>

            <h2 className="about-h2">Claude Code / linha de comando</h2>
            <pre className="mcp-code">
              <code>claude mcp add --transport http arandu {MCP_URL}</code>
            </pre>

            <h2 className="about-h2">Ou em mcp.json</h2>
            <pre className="mcp-code">
              <code>{`{
  "mcpServers": {
    "arandu": { "url": "${MCP_URL}" }
  }
}`}</code>
            </pre>

            <h2 className="about-h2">Ferramentas disponíveis</h2>
            <ul className="about-list">
              <li>
                <code>list_series</code> — o catálogo: nome, fonte, unidade, frequência, último valor.
              </li>
              <li>
                <code>search_series(query)</code> — busca por palavra-chave nas séries.
              </li>
              <li>
                <code>get_series(series_id, start_date?, end_date?)</code> — metadados e as
                observações por trás de um gráfico.
              </li>
              <li>
                <code>get_series_sources</code> — as instituições e fontes, com URLs públicas.
              </li>
            </ul>

            <ul className="about-links">
              <li>
                <a
                  href={`${REPO}/blob/main/metasystemic/agent-interface.md`}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Interface para agentes ↗
                </a>
              </li>
            </ul>

            <p className="about-foot">Somente leitura · mesma lente, respondida ao vivo</p>
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
            <p className="about-sub">Consulta Cívica — uma lente pública para o Brasil</p>

            <p>
              O Arandu reúne os dados fiscais e econômicos do Brasil em um só lugar, sempre
              com a fonte à vista. É um projeto aberto: qualquer pessoa pode olhar os mesmos
              números e tirar as próprias conclusões.
            </p>
            <p>
              Não pertence a nenhum partido, campanha, ministério ou jornal. É um instrumento
              cívico — a ideia não é dizer o que pensar sobre os números, e sim deixar claro de
              onde eles vêm, para que qualquer um possa conferir.
            </p>
            <p>
              Cada gráfico mostra de onde vem o dado, como foi calculado, quando foi atualizado
              e o que vale a pena observar com atenção.
            </p>

            <h2 className="about-h2">Como usar</h2>
            <p>
              Clique em qualquer gráfico para abri-lo em tela cheia. Ali você pode mudar a
              visualização — tabela, pizza, linha, barra — e suas escolhas ficam salvas no seu
              navegador. Use o filtro de período no topo para recortar o tempo e o ícone de
              download para baixar todas as séries.
            </p>

            <h2 className="about-h2">O projeto</h2>
            <p>
              Código aberto, dados abertos, método público. O Arandu é mantido publicamente no
              GitHub e segue uma constituição que define como ele muda e como os dados entram.
            </p>
            <ul className="about-links">
              <li>
                <a href={REPO} target="_blank" rel="noopener noreferrer">
                  Repositório ↗
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

            <p className="about-foot">v0.1 · Brasil</p>
          </div>
        </div>
      )}
    </main>
  );
}
