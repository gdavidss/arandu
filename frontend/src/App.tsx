import { useEffect, useRef, useState } from "react";

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

type Active = { id: string; title: string; src: string };

export function App() {
  const [dashboardUrl, setDashboardUrl] = useState("");
  const [questionEditByName, setQuestionEditByName] = useState<Record<string, string>>({});
  const [active, setActive] = useState<Active | null>(null);
  const [showAbout, setShowAbout] = useState(false);
  const frameRef = useRef<HTMLIFrameElement | null>(null);
  const embedUrl = metabaseDashboardUrl(dashboardUrl);

  const REPO = "https://github.com/gdavidss/arandu";

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
  // We open the card's real Metabase question (the native visualization editor — table,
  // pie, bar, settings, everything), restoring the user's previously saved view if any.
  // NOTE the storage key is versioned (viz2): the v1 entries saved paths without the
  // /metabase proxy prefix (Metabase's SPA rewrites its URL client-side without it),
  // which restored to a broken route stuck on "Carregando…".
  useEffect(() => {
    function onMessage(event: MessageEvent) {
      const data = event.data;
      if (!data || data.type !== "fiscallens-card-zoom") return;
      const editUrl = questionEditByName[data.title];
      const id = editUrl ? cardId(editUrl) : null;
      if (!editUrl || !id) return;
      const saved = localStorage.getItem(`arandu:viz2:${id}`);
      const valid = saved && saved.startsWith("/metabase/") && saved.includes("/question");
      setActive({ id, title: data.title, src: valid ? saved : proxiedQuestion(editUrl) });
    }
    window.addEventListener("message", onMessage);
    return () => window.removeEventListener("message", onMessage);
  }, [questionEditByName]);

  // While the editor is open, persist the question's view (Metabase serializes the chosen
  // visualization into the URL) to localStorage, so the user's choice sticks per card.
  // The SPA drops the /metabase proxy prefix when it rewrites the URL — re-add it.
  useEffect(() => {
    if (!active) return;
    const id = active.id;
    const tick = () => {
      try {
        const win = frameRef.current?.contentWindow;
        if (!win) return;
        const loc = win.location;
        let rel = `${loc.pathname}${loc.search}${loc.hash}`;
        if (!rel.startsWith("/metabase/")) rel = `/metabase${rel}`;
        if (rel.includes("/question") && !rel.includes("/auth/login")) {
          localStorage.setItem(`arandu:viz2:${id}`, rel);
        }
      } catch {
        // cross-origin during a redirect; ignore.
      }
    };
    const iv = window.setInterval(tick, 800);
    return () => window.clearInterval(iv);
  }, [active]);

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
            <iframe
              ref={frameRef}
              className="zoom-frame"
              src={active.src}
              title={active.title}
            />
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
