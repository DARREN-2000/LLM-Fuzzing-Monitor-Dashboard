const sessionRows = document.getElementById("sessionRows");
const kpis = document.getElementById("kpis");
const providerBars = document.getElementById("providerBars");
const statusText = document.getElementById("status");
const fileInput = document.getElementById("sessionFiles");
const loadSampleBtn = document.getElementById("loadSample");

function toNumber(value) {
  const n = Number(value);
  return Number.isFinite(n) ? n : 0;
}

function parseSession(payload) {
  if (!payload || typeof payload !== "object") return null;
  if (!payload.session_id) return null;
  return {
    session_id: String(payload.session_id),
    llm_provider: String(payload.llm_provider ?? "unknown"),
    llm_model: String(payload.llm_model ?? "unknown"),
    status: String(payload.status ?? "unknown"),
    fuzz_drivers_generated: toNumber(payload.fuzz_drivers_generated),
    security_vulnerabilities_found: toNumber(payload.security_vulnerabilities_found),
    total_duration_ms: toNumber(payload.total_duration_ms),
    estimated_cost_usd: toNumber(payload.estimated_cost_usd),
    total_tokens_consumed: toNumber(payload.total_tokens_consumed),
    total_api_calls: toNumber(payload.total_api_calls),
  };
}

function formatCurrency(value) {
  return `$${value.toFixed(2)}`;
}

function render(data) {
  const sessions = data.filter(Boolean);

  const totalSessions = sessions.length;
  const totalDrivers = sessions.reduce((s, x) => s + x.fuzz_drivers_generated, 0);
  const totalVulns = sessions.reduce((s, x) => s + x.security_vulnerabilities_found, 0);
  const totalCost = sessions.reduce((s, x) => s + x.estimated_cost_usd, 0);
  const totalDurationHours = sessions.reduce((s, x) => s + x.total_duration_ms, 0) / 3_600_000;
  const totalTokens = sessions.reduce((s, x) => s + x.total_tokens_consumed, 0);

  kpis.innerHTML = [
    ["Sessions", totalSessions],
    ["Drivers", totalDrivers],
    ["Vulnerabilities", totalVulns],
    ["Duration (h)", totalDurationHours.toFixed(2)],
    ["Cost (USD)", formatCurrency(totalCost)],
    ["Tokens", totalTokens.toLocaleString()],
  ]
    .map(([label, value]) => `<div class="kpi"><div class="label">${label}</div><div class="value">${value}</div></div>`)
    .join("");

  const providerCounts = sessions.reduce((acc, s) => {
    acc[s.llm_provider] = (acc[s.llm_provider] ?? 0) + 1;
    return acc;
  }, {});

  const maxProviderCount = Math.max(1, ...Object.values(providerCounts));
  providerBars.innerHTML = Object.entries(providerCounts)
    .sort((a, b) => b[1] - a[1])
    .map(([provider, count]) => {
      const width = (count / maxProviderCount) * 100;
      return `<div class="bar-row"><span>${provider}</span><div class="bar" style="width:${width}%"></div><span>${count}</span></div>`;
    })
    .join("");

  sessionRows.innerHTML = sessions
    .map(
      (s) => `<tr>
      <td>${s.session_id}</td>
      <td>${s.llm_provider}</td>
      <td>${s.llm_model}</td>
      <td>${s.status}</td>
      <td>${s.fuzz_drivers_generated}</td>
      <td>${s.security_vulnerabilities_found}</td>
      <td>${(s.total_duration_ms / 3_600_000).toFixed(2)}</td>
      <td>${formatCurrency(s.estimated_cost_usd)}</td>
    </tr>`,
    )
    .join("");
}

async function loadSampleData() {
  try {
    const res = await fetch("./sample-data/sessions.json", { cache: "no-store" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const payload = await res.json();
    const sessions = Array.isArray(payload) ? payload.map(parseSession).filter(Boolean) : [];
    render(sessions);
    statusText.textContent = `Loaded ${sessions.length} sample sessions.`;
  } catch (error) {
    statusText.textContent = `Failed to load sample data: ${String(error)}`;
  }
}

async function loadUploadedFiles(files) {
  const sessions = [];

  for (const file of files) {
    if (!file.name.toLowerCase().endsWith(".json")) continue;
    try {
      const content = await file.text();
      const parsed = JSON.parse(content);
      const session = parseSession(parsed);
      if (session) sessions.push(session);
    } catch {
      // Skip invalid JSON files.
    }
  }

  if (sessions.length === 0) {
    statusText.textContent = "No valid session.json files were found in the upload.";
    return;
  }

  render(sessions);
  statusText.textContent = `Loaded ${sessions.length} uploaded sessions.`;
}

fileInput.addEventListener("change", () => {
  if (fileInput.files?.length) {
    loadUploadedFiles(fileInput.files);
  }
});

loadSampleBtn.addEventListener("click", () => {
  loadSampleData();
});

loadSampleData();
