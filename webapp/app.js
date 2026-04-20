const sessionRows = document.getElementById("sessionRows");
const kpis = document.getElementById("kpis");
const providerBars = document.getElementById("providerBars");
const statusText = document.getElementById("status");
const fileInput = document.getElementById("sessionFiles");
const loadSampleBtn = document.getElementById("loadSample");
const clearDataBtn = document.getElementById("clearData");
const providerFilter = document.getElementById("providerFilter");
const statusFilter = document.getElementById("statusFilter");
const sortBy = document.getElementById("sortBy");
const emptyState = document.getElementById("emptyState");

/** @type {Array<ReturnType<typeof parseSession>>} */
let allSessions = [];

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

function parsePayload(payload) {
  if (Array.isArray(payload)) {
    return payload.map(parseSession).filter(Boolean);
  }

  const single = parseSession(payload);
  return single ? [single] : [];
}

function formatCurrency(value) {
  return `$${value.toFixed(2)}`;
}

function setStatus(text, isError = false) {
  statusText.textContent = text;
  statusText.style.color = isError ? "#ff7a7a" : "#39d98a";
}

function setOptions(selectEl, values, allLabel) {
  const current = selectEl.value;
  selectEl.replaceChildren();

  const all = document.createElement("option");
  all.value = "all";
  all.textContent = allLabel;
  selectEl.appendChild(all);

  values.forEach((value) => {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = value;
    selectEl.appendChild(option);
  });

  if (["all", ...values].includes(current)) {
    selectEl.value = current;
  }
}

function sortSessions(sessions) {
  const selected = sortBy.value;
  const sorted = [...sessions];

  const by = {
    duration: (s) => s.total_duration_ms,
    cost: (s) => s.estimated_cost_usd,
    vulns: (s) => s.security_vulnerabilities_found,
    drivers: (s) => s.fuzz_drivers_generated,
  };

  const key = by[selected] ?? by.duration;
  sorted.sort((a, b) => key(b) - key(a));
  return sorted;
}

function getFilteredSessions() {
  let sessions = allSessions;

  if (providerFilter.value !== "all") {
    sessions = sessions.filter((s) => s.llm_provider === providerFilter.value);
  }

  if (statusFilter.value !== "all") {
    sessions = sessions.filter((s) => s.status === statusFilter.value);
  }

  return sortSessions(sessions);
}

function renderKpis(sessions) {
  const totalSessions = sessions.length;
  const totalDrivers = sessions.reduce((s, x) => s + x.fuzz_drivers_generated, 0);
  const totalVulns = sessions.reduce((s, x) => s + x.security_vulnerabilities_found, 0);
  const totalCost = sessions.reduce((s, x) => s + x.estimated_cost_usd, 0);
  const totalDurationHours = sessions.reduce((s, x) => s + x.total_duration_ms, 0) / 3_600_000;
  const totalTokens = sessions.reduce((s, x) => s + x.total_tokens_consumed, 0);

  const cards = [
    ["Sessions", totalSessions.toLocaleString()],
    ["Drivers", totalDrivers.toLocaleString()],
    ["Vulnerabilities", totalVulns.toLocaleString()],
    ["Duration (h)", totalDurationHours.toFixed(2)],
    ["Cost (USD)", formatCurrency(totalCost)],
    ["Tokens", totalTokens.toLocaleString()],
  ];

  kpis.replaceChildren();

  cards.forEach(([label, value]) => {
    const card = document.createElement("div");
    card.className = "kpi";

    const labelEl = document.createElement("div");
    labelEl.className = "label";
    labelEl.textContent = label;

    const valueEl = document.createElement("div");
    valueEl.className = "value";
    valueEl.textContent = value;

    card.appendChild(labelEl);
    card.appendChild(valueEl);
    kpis.appendChild(card);
  });
}

function renderProviders(sessions) {
  const providerCounts = sessions.reduce((acc, s) => {
    acc[s.llm_provider] = (acc[s.llm_provider] ?? 0) + 1;
    return acc;
  }, {});

  const entries = Object.entries(providerCounts).sort((a, b) => b[1] - a[1]);
  const maxProviderCount = Math.max(1, ...entries.map((x) => x[1]));

  providerBars.replaceChildren();

  for (const [provider, count] of entries) {
    const row = document.createElement("div");
    row.className = "bar-row";

    const providerLabel = document.createElement("span");
    providerLabel.textContent = provider;

    const bar = document.createElement("div");
    bar.className = "bar";
    bar.style.width = `${(count / maxProviderCount) * 100}%`;

    const countLabel = document.createElement("span");
    countLabel.textContent = String(count);

    row.appendChild(providerLabel);
    row.appendChild(bar);
    row.appendChild(countLabel);

    providerBars.appendChild(row);
  }
}

function renderRows(sessions) {
  sessionRows.replaceChildren();

  for (const s of sessions) {
    const row = document.createElement("tr");

    [
      s.session_id,
      s.llm_provider,
      s.llm_model,
      s.status,
      s.fuzz_drivers_generated,
      s.security_vulnerabilities_found,
      (s.total_duration_ms / 3_600_000).toFixed(2),
      formatCurrency(s.estimated_cost_usd),
    ].forEach((value) => {
      const cell = document.createElement("td");
      cell.textContent = String(value);
      row.appendChild(cell);
    });

    sessionRows.appendChild(row);
  }
}

function render() {
  const filtered = getFilteredSessions();
  emptyState.classList.toggle("hidden", filtered.length > 0);
  renderKpis(filtered);
  renderProviders(filtered);
  renderRows(filtered);
}

function refreshFilters() {
  const providers = [...new Set(allSessions.map((s) => s.llm_provider))].sort();
  const statuses = [...new Set(allSessions.map((s) => s.status))].sort();
  setOptions(providerFilter, providers, "All providers");
  setOptions(statusFilter, statuses, "All statuses");
}

function setSessions(sessions, sourceName) {
  allSessions = sessions;
  refreshFilters();
  render();
  setStatus(`Loaded ${sessions.length} session(s) from ${sourceName}.`);
}

async function loadSampleData() {
  try {
    const res = await fetch("./sample-data/sessions.json", { cache: "no-store" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const payload = await res.json();
    const sessions = parsePayload(payload);

    if (sessions.length === 0) {
      throw new Error("sample-data/sessions.json has no valid sessions");
    }

    setSessions(sessions, "sample data");
  } catch (error) {
    setStatus(`Failed to load sample data: ${String(error)}`, true);
  }
}

async function loadUploadedFiles(files) {
  const sessions = [];

  for (const file of files) {
    if (!file.name.toLowerCase().endsWith(".json")) continue;

    try {
      const content = await file.text();
      const parsed = JSON.parse(content);
      sessions.push(...parsePayload(parsed));
    } catch {
      // Skip invalid JSON files.
    }
  }

  if (sessions.length === 0) {
    setStatus("No valid session JSON files were found in the upload.", true);
    return;
  }

  setSessions(sessions, "uploaded files");
}

function clearData() {
  allSessions = [];
  refreshFilters();
  render();
  setStatus("Cleared all loaded sessions.");
}

fileInput.addEventListener("change", () => {
  if (fileInput.files?.length) {
    loadUploadedFiles(fileInput.files);
  }
});

providerFilter.addEventListener("change", render);
statusFilter.addEventListener("change", render);
sortBy.addEventListener("change", render);
loadSampleBtn.addEventListener("click", loadSampleData);
clearDataBtn.addEventListener("click", clearData);

loadSampleData();
