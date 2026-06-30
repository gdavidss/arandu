import { createReadStream, existsSync } from "node:fs";
import { stat } from "node:fs/promises";
import { createServer } from "node:http";
import { extname, join, normalize, resolve } from "node:path";

const root = resolve("dist");
const publicRoot = resolve("public");
const port = Number(process.env.PORT || 5173);
const host = process.env.HOST || "0.0.0.0";
const metabaseInternalUrl = process.env.METABASE_INTERNAL_URL || "http://localhost:3000";
const metabaseProxyPrefixes = ["/metabase/", "/api/", "/app/", "/public/", "/favicon.ico"];

// The proxy carries a Metabase session so the embedded, editable question view works
// without a login wall. Credentials stay server-side here (never in the browser). For a
// public deployment you'd swap this for a restricted embedding user; locally it's the
// instance's own admin. The session is attached to upstream requests as a cookie.
const mbEmail = process.env.MB_EMAIL || "admin@fiscallens.local";
const mbPassword = process.env.MB_PASSWORD || "FiscalLensBrasil2026!";
let mbSessionId = null;
let mbSessionPromise = null;

async function getMetabaseSession() {
  if (mbSessionId) return mbSessionId;
  if (!mbEmail || !mbPassword) return null;
  if (!mbSessionPromise) {
    mbSessionPromise = fetch(`${metabaseInternalUrl}/api/session`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ username: mbEmail, password: mbPassword }),
    })
      .then((r) => (r.ok ? r.json() : null))
      .then((j) => (j && j.id ? j.id : null))
      .catch(() => null)
      .then((id) => {
        mbSessionId = id;
        mbSessionPromise = null;
        return id;
      });
  }
  return mbSessionPromise;
}

function clearMetabaseSession() {
  mbSessionId = null;
}

const metabaseEmbedCleanup = `
<style id="fiscallens-metabase-embed-cleanup">
  [role="contentinfo"],
  footer,
  a[href*="powered_by_metabase"],
  .EmbedFrame-footer,
  .PoweredByMetabase {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    min-height: 0 !important;
    overflow: hidden !important;
  }
  /* Full-bleed: drop Metabase's large centered page margins; use the full width. */
  .EmbedFrame,
  .EmbedFrame-body,
  [class*="EmbedFrame"],
  [class*="DashboardContainer"],
  [class*="DashboardGridContainer"],
  [data-testid="embed-frame"],
  [data-testid="fixed-width-dashboard-header"],
  [data-testid="fixed-width-dashboard-tabs"],
  [data-testid="fixed-width-filters"] {
    max-width: 100% !important;
    margin-left: 0 !important;
    margin-right: 0 !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
  }
  /* Cards keep a small even gutter from the edge so they don't glue to the window.
     Generous bottom padding so the last row clears the ~96px the parent clips to hide
     Metabase's footer — otherwise the bottom cards get cut off. */
  [data-testid="dashboard-grid"],
  [class*="DashboardGrid"] {
    padding: 4px 20px 140px !important;
    max-width: 100% !important;
  }
  /* Filter bar: white at the top (seamless with the header) fading DOWN into gray.
     The grid/content below carries the same gray so there's no line. */
  [data-testid="dashboard-parameters-widget-container"] {
    padding: 14px 20px 26px !important;
    margin: 0 !important;
    background: linear-gradient(to bottom, #ffffff 0px, #eceee9 22px) !important;
    border: 0 !important;
    box-shadow: none !important;
  }
  /* Kill any separator line/shadow Metabase draws around the header/filter/grid region. */
  [data-testid="fixed-width-dashboard-header"],
  [data-testid="dashboard-header"],
  [data-testid="embed-frame"],
  [class*="EmbedFrame"],
  [data-testid="dashboard-grid"] {
    border-top: 0 !important;
    border-bottom: 0 !important;
    box-shadow: none !important;
  }
  /* Hide the stray embed header action icons (fullscreen / export / refresh). */
  [aria-label="fullscreen"],
  [aria-label*="Tela cheia"],
  [data-testid="export-as-pdf-button"],
  .DashboardActions {
    display: none !important;
  }
  /* Center the tab strip in the navbar. The wordmark is an absolute ::before (out of flow),
     so centering ignores it. "safe center" keeps tabs reachable if they overflow. */
  [data-testid="fixed-width-dashboard-tabs"] {
    display: flex !important;
    justify-content: safe center !important;
    /* Symmetric room so the strip stays truly centered and clears the left wordmark. */
    padding-left: 132px !important;
    padding-right: 132px !important;
  }
  [data-testid="fixed-width-dashboard-tabs"] > div,
  [role="tablist"] {
    flex: 1 1 auto !important;
    width: 100% !important;
    display: flex !important;
    justify-content: safe center !important;
  }
  /* Center the filter widgets (Período / De / Até) like the tabs. */
  [data-testid="dashboard-parameters-widget-container"] {
    display: flex !important;
    justify-content: safe center !important;
  }
  [data-testid="fixed-width-filters"] {
    display: flex !important;
    justify-content: safe center !important;
  }
  /* Brand wordmark on the far left of the tab navbar (absolute, out of flow). */
  [data-testid="fixed-width-dashboard-tabs"] {
    position: relative !important;
  }
  [data-testid="fixed-width-dashboard-tabs"]::before {
    content: "Arandu";
    position: absolute;
    left: 20px;
    top: 50%;
    transform: translateY(-50%);
    font-family: inherit;
    font-weight: 700;
    font-size: 19px;
    letter-spacing: -0.2px;
    color: #1f2937; /* neutral dark */
    pointer-events: none;
    white-space: nowrap;
  }
  /* Per-card source logo (added by script), sits left of the "…" menu. */
  a.fl-source {
    display: inline-flex;
    align-items: center;
    margin-right: 4px;
    opacity: 0.65;
    font-size: 11px;
    font-weight: 600;
    color: #6b7280;
    text-decoration: none;
    cursor: alias;
  }
  a.fl-source:hover {
    opacity: 1;
  }
  a.fl-source img {
    display: block;
    width: 16px;
    height: 16px;
    border-radius: 3px;
  }
  /* Cards: white tiles on the gray canvas. Clickable to open full-screen. */
  [data-testid="dashcard"] {
    cursor: zoom-in;
    background: #ffffff !important;
    border: 1px solid #e2e4df !important;
    border-radius: 12px !important;
    box-shadow: 0 1px 2px rgba(20, 30, 20, 0.04) !important;
    overflow: hidden;
  }
  /* Editable question view (full app, shown in the card modal): trim the global chrome so
     the modal is mostly the chart and Metabase's own visualization editor. */
  [data-testid="main-navbar-root"],
  [data-element-id="navbar-root"],
  [data-testid="app-bar"] {
    display: none !important;
  }
  /* Mobile: tighter side gutters so stacked cards use the width. */
  @media (max-width: 640px) {
    [data-testid="dashboard-grid"],
    [class*="DashboardGrid"] {
      padding-left: 8px !important;
      padding-right: 8px !important;
    }
    [data-testid="dashboard-parameters-widget-container"] {
      padding-left: 10px !important;
      padding-right: 10px !important;
    }
  }
</style>
<script id="fiscallens-card-zoom">
(function () {
  if (window.__flCardZoom) return;
  window.__flCardZoom = true;
  document.addEventListener(
    "click",
    function (event) {
      var el = event.target;
      // Let the per-card source logo behave as a normal link, not a zoom trigger.
      if (el && el.closest && el.closest("a.fl-source")) return;
      var card = el && el.closest ? el.closest('[data-testid="dashcard"]') : null;
      if (!card) return;
      var titleEl = card.querySelector('[data-testid="legend-caption-title"]');
      var title = titleEl && titleEl.textContent ? titleEl.textContent.trim() : "";
      if (!title) return;
      event.preventDefault();
      event.stopPropagation();
      window.parent.postMessage({ type: "fiscallens-card-zoom", title: title }, "*");
    },
    true,
  );
})();
</script>
<script id="fiscallens-card-source">
(function () {
  if (window.__flCardSource) return;
  window.__flCardSource = true;
  var MAP = null;
  function decorate(card) {
    if (card.querySelector("a.fl-source")) return;
    var titleEl = card.querySelector('[data-testid="legend-caption-title"]');
    var title = titleEl && titleEl.textContent ? titleEl.textContent.trim() : "";
    var src = MAP && MAP[title];
    if (!src) return;
    // Only place the logo immediately left of the "…" menu. If the menu hasn't rendered
    // yet, skip — the MutationObserver will retry once it appears (avoids a stray
    // bottom-of-card placement).
    var menu = card.querySelector('[data-testid="public-or-embedded-dashcard-menu"]');
    if (!menu || !menu.parentNode) return;
    var a = document.createElement("a");
    a.className = "fl-source";
    a.href = src.url;
    a.target = "_blank";
    a.rel = "noopener noreferrer";
    a.title = "Fonte: " + src.label + " — abrir site";
    var img = document.createElement("img");
    img.src = "https://www.google.com/s2/favicons?domain=" + src.domain + "&sz=32";
    img.alt = src.label;
    img.onerror = function () {
      if (img.parentNode) a.removeChild(img);
      a.textContent = src.label;
    };
    a.appendChild(img);
    menu.parentNode.insertBefore(a, menu);
  }
  function decorateAll() {
    if (!MAP) return;
    var cards = document.querySelectorAll('[data-testid="dashcard"]');
    for (var i = 0; i < cards.length; i++) decorate(cards[i]);
  }
  fetch("/metabase-dashboards.json")
    .then(function (r) { return r.json(); })
    .then(function (d) { MAP = d.card_sources || {}; decorateAll(); })
    .catch(function () {});
  var mo = new MutationObserver(function () { decorateAll(); });
  mo.observe(document.documentElement, { childList: true, subtree: true });
})();
</script>`;

const contentTypes = new Map([
  [".csv", "text/csv; charset=utf-8"],
  [".css", "text/css; charset=utf-8"],
  [".html", "text/html; charset=utf-8"],
  [".js", "text/javascript; charset=utf-8"],
  [".json", "application/json; charset=utf-8"],
  [".png", "image/png"],
  [".svg", "image/svg+xml"],
]);

function resolveRequestPath(url) {
  const parsed = new URL(url || "/", `http://${host}:${port}`);
  const safePath = normalize(decodeURIComponent(parsed.pathname)).replace(/^(\.\.[/\\])+/, "");
  if (safePath !== "/") {
    const publicPath = join(publicRoot, safePath);
    if (publicPath.startsWith(publicRoot) && existsSync(publicPath)) return publicPath;
  }
  const filePath = join(root, safePath === "/" ? "index.html" : safePath);
  if (!filePath.startsWith(root)) return join(root, "index.html");
  return filePath;
}

function isMetabaseProxyPath(pathname) {
  return metabaseProxyPrefixes.some((prefix) => pathname === prefix || pathname.startsWith(prefix));
}

async function requestBody(request) {
  if (request.method === "GET" || request.method === "HEAD") return undefined;

  const chunks = [];
  for await (const chunk of request) {
    chunks.push(chunk);
  }
  return chunks.length ? Buffer.concat(chunks) : undefined;
}

function proxyPath(pathname) {
  if (pathname.startsWith("/metabase/")) {
    return pathname.slice("/metabase".length) || "/";
  }
  return pathname;
}

async function proxyMetabase(request, response) {
  const incoming = new URL(request.url || "/", `http://${host}:${port}`);
  const target = new URL(proxyPath(incoming.pathname) + incoming.search, metabaseInternalUrl);
  const headers = new Headers(request.headers);
  headers.set("host", target.host);

  // Attach the server-side Metabase session so editable question views are authenticated —
  // but NOT for public routes. The main dashboard is a public embed; attaching a session to
  // /public/* or /api/public/* makes Metabase expect an authenticated (CSRF) flow and the
  // public queries hang ("Carregando…"). Keep those anonymous; authenticate everything else.
  const upstreamPath = target.pathname;
  const isPublicRoute =
    upstreamPath.startsWith("/public/") ||
    upstreamPath.startsWith("/api/public/") ||
    upstreamPath.startsWith("/api/embed/");
  if (!isPublicRoute) {
    const session = await getMetabaseSession();
    if (session) {
      const existing = headers.get("cookie");
      headers.set("cookie", `${existing ? existing + "; " : ""}metabase.SESSION=${session}`);
    }
  }

  const upstream = await fetch(target, {
    method: request.method,
    headers,
    body: await requestBody(request),
    redirect: "manual",
  });

  // If the session went stale, drop it so the next request logs in again.
  if (upstream.status === 401 || upstream.status === 403) clearMetabaseSession();

  const responseHeaders = {};
  upstream.headers.forEach((value, key) => {
    const lowered = key.toLowerCase();
    if (
      lowered === "content-security-policy" ||
      lowered === "content-encoding" ||
      lowered === "content-length" ||
      lowered === "transfer-encoding" ||
      lowered === "x-frame-options"
    ) {
      return;
    }
    if (lowered === "location") {
      responseHeaders[key] = value.replace(metabaseInternalUrl, "/metabase");
      return;
    }
    responseHeaders[key] = value;
  });
  responseHeaders["Cache-Control"] = "no-store";

  const contentType = upstream.headers.get("content-type") || "";
  if (contentType.includes("text/html")) {
    let html = await upstream.text();
    html = html.includes("</head>")
      ? html.replace("</head>", `${metabaseEmbedCleanup}</head>`)
      : `${metabaseEmbedCleanup}${html}`;
    response.writeHead(upstream.status, {
      ...responseHeaders,
      "Content-Type": contentType,
    });
    response.end(html);
    return;
  }

  const bytes = Buffer.from(await upstream.arrayBuffer());
  response.writeHead(upstream.status, responseHeaders);
  response.end(bytes);
}

const server = createServer(async (request, response) => {
  const parsed = new URL(request.url || "/", `http://${host}:${port}`);
  if (isMetabaseProxyPath(parsed.pathname)) {
    try {
      await proxyMetabase(request, response);
    } catch (error) {
      console.error("Metabase proxy failed", error);
      response.writeHead(502, { "Content-Type": "text/plain; charset=utf-8" });
      response.end("Metabase proxy failed");
    }
    return;
  }

  let filePath = resolveRequestPath(request.url);
  try {
    const fileStat = await stat(filePath);
    if (fileStat.isDirectory()) filePath = join(filePath, "index.html");
  } catch {
    if (extname(filePath)) {
      response.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" });
      response.end("Not found");
      return;
    }
    filePath = join(root, "index.html");
  }

  if (!existsSync(filePath)) {
    response.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" });
    response.end("Not found");
    return;
  }

  response.writeHead(200, {
    "Cache-Control": "no-store",
    "Content-Type": contentTypes.get(extname(filePath)) || "application/octet-stream",
  });
  createReadStream(filePath).pipe(response);
});

server.listen(port, host, () => {
  console.log(`arandu.ai frontend listening on http://${host}:${port}`);
});
