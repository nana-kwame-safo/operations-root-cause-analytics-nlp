const domainSelect = document.getElementById("domainSelect");
const thresholdInput = document.getElementById("thresholdInput");
const thresholdValue = document.getElementById("thresholdValue");
const topKInput = document.getElementById("topKInput");
const narrativeInput = document.getElementById("narrativeInput");
const predictBtn = document.getElementById("predictBtn");
const predictStatus = document.getElementById("predictStatus");

const resultCount = document.getElementById("resultCount");
const topScore = document.getElementById("topScore");
const reviewFlagChip = document.getElementById("reviewFlagChip");
const reviewFlagValue = document.getElementById("reviewFlagValue");
const reviewBanner = document.getElementById("reviewBanner");
const artifactBanner = document.getElementById("artifactBanner");

const predictionSummaryText = document.getElementById("predictionSummaryText");
const summaryPills = document.getElementById("summaryPills");
const plainExplanationText = document.getElementById("plainExplanationText");
const evidenceNarrative = document.getElementById("evidenceNarrative");
const analystExplanation = document.getElementById("analystExplanation");
const alternativesBody = document.getElementById("alternativesBody");
const feedbackStatus = document.getElementById("feedbackStatus");
const feedbackButtons = document.querySelectorAll(".feedback-btn");

const simpleViewBtn = document.getElementById("simpleViewBtn");
const analystViewBtn = document.getElementById("analystViewBtn");
const themeSelect = document.getElementById("themeSelect");

const batchFile = document.getElementById("batchFile");
const batchBtn = document.getElementById("batchBtn");
const downloadBtn = document.getElementById("downloadBtn");
const batchStatus = document.getElementById("batchStatus");
const textColumnInput = document.getElementById("textColumnInput");
const batchRows = document.getElementById("batchRows");
const batchAvgLabels = document.getElementById("batchAvgLabels");
const batchReviewCount = document.getElementById("batchReviewCount");
const batchResultsBody = document.getElementById("batchResultsBody");

const modelInfo = document.getElementById("modelInfo");

const THEME_STORAGE_KEY = "orca_nlp_theme_mode";
const RESULT_VIEW_STORAGE_KEY = "orca_nlp_result_view";
const DEFAULT_RESULTS_MESSAGE = "No prediction results yet. Enter a narrative and run scoring.";
const DEFAULT_BATCH_MESSAGE = "No batch results yet. Upload a CSV and run batch prediction.";
const themeMediaQuery = window.matchMedia("(prefers-color-scheme: dark)");

const urlParams = new URLSearchParams(window.location.search);
const demoMode = (urlParams.get("demo") || "").toLowerCase();
const forcedViewMode = (urlParams.get("mode") || "").toLowerCase();
const forcedThemeMode = (urlParams.get("theme") || "").toLowerCase();

let selectedThemeMode = "system";
let selectedResultView = "simple";
let lastBatchResults = [];
let isPredicting = false;
let isBatchRunning = false;

thresholdInput.addEventListener("input", () => {
  thresholdValue.textContent = Number(thresholdInput.value).toFixed(2);
});

function resolveTheme(mode) {
  if (mode === "system") {
    return themeMediaQuery.matches ? "dark" : "light";
  }
  return mode;
}

function applyTheme(mode) {
  selectedThemeMode = mode;
  const resolved = resolveTheme(mode);
  document.documentElement.dataset.theme = resolved;
  document.documentElement.dataset.themeMode = mode;
  themeSelect.value = mode;
}

function initTheme() {
  let mode = "system";
  if (["light", "dark", "system"].includes(forcedThemeMode)) {
    mode = forcedThemeMode;
  } else {
    try {
      const saved = localStorage.getItem(THEME_STORAGE_KEY);
      mode = ["light", "dark", "system"].includes(saved) ? saved : "system";
    } catch (_err) {
      mode = "system";
    }
  }
  applyTheme(mode);

  themeSelect.addEventListener("change", () => {
    const next = themeSelect.value;
    try {
      localStorage.setItem(THEME_STORAGE_KEY, next);
    } catch (_err) {
      // Ignore localStorage errors.
    }
    applyTheme(next);
  });

  themeMediaQuery.addEventListener("change", () => {
    if (selectedThemeMode === "system") {
      applyTheme("system");
    }
  });
}

function setResultView(mode) {
  selectedResultView = mode === "analyst" ? "analyst" : "simple";
  document.body.dataset.resultView = selectedResultView;
  simpleViewBtn.classList.toggle("active", selectedResultView === "simple");
  analystViewBtn.classList.toggle("active", selectedResultView === "analyst");
}

function initResultView() {
  let mode = "simple";
  if (["simple", "analyst"].includes(forcedViewMode)) {
    mode = forcedViewMode;
  } else {
    try {
      const saved = localStorage.getItem(RESULT_VIEW_STORAGE_KEY);
      mode = ["simple", "analyst"].includes(saved) ? saved : "simple";
    } catch (_err) {
      mode = "simple";
    }
  }

  setResultView(mode);
  simpleViewBtn.addEventListener("click", () => {
    setResultView("simple");
    try {
      localStorage.setItem(RESULT_VIEW_STORAGE_KEY, "simple");
    } catch (_err) {
      // Ignore localStorage errors.
    }
  });
  analystViewBtn.addEventListener("click", () => {
    setResultView("analyst");
    try {
      localStorage.setItem(RESULT_VIEW_STORAGE_KEY, "analyst");
    } catch (_err) {
      // Ignore localStorage errors.
    }
  });
}

function setBanner(text, tone) {
  reviewBanner.classList.remove("hidden", "ok", "review", "error", "info");
  reviewBanner.classList.add(tone);
  reviewBanner.textContent = text;
}

function setArtifactBanner(status) {
  artifactBanner.classList.remove("hidden", "ok", "review", "error", "info");
  if (status === "available") {
    artifactBanner.classList.add("ok");
    artifactBanner.textContent = "Model artifact loaded. Live prediction is available.";
    return;
  }
  artifactBanner.classList.add("review");
  artifactBanner.textContent =
    "Model artifact not loaded. The UI, metadata, and API are live; full prediction requires the trained aviation model artifact.";
}

function setReviewChip(value, tone = "neutral") {
  reviewFlagChip.classList.remove("chip-neutral", "chip-ok", "chip-review", "chip-error");
  if (tone === "ok") {
    reviewFlagChip.classList.add("chip-ok");
  } else if (tone === "review") {
    reviewFlagChip.classList.add("chip-review");
  } else if (tone === "error") {
    reviewFlagChip.classList.add("chip-error");
  } else {
    reviewFlagChip.classList.add("chip-neutral");
  }
  reviewFlagValue.textContent = value;
}

function setPredictStatus(text, tone = "") {
  predictStatus.classList.remove("success", "warn", "error");
  if (tone) predictStatus.classList.add(tone);
  predictStatus.textContent = text;
}

function setBatchStatus(text, tone = "") {
  batchStatus.classList.remove("success", "warn", "error");
  if (tone) batchStatus.classList.add(tone);
  batchStatus.textContent = text;
}

function setPredictLoading(isLoading) {
  isPredicting = isLoading;
  predictBtn.disabled = isLoading;
  predictBtn.classList.toggle("loading", isLoading);
  const label = predictBtn.querySelector("span:last-child");
  label.textContent = isLoading ? "Scoring Narrative..." : "Predict Factors";
}

function setBatchLoading(isLoading) {
  isBatchRunning = isLoading;
  batchBtn.disabled = isLoading;
  batchBtn.classList.toggle("loading", isLoading);
  const label = batchBtn.querySelector("span:last-child");
  label.textContent = isLoading ? "Scoring Batch..." : "Run Batch Prediction";
}

function escapeHtml(text) {
  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function renderAlternativesEmpty(text) {
  alternativesBody.innerHTML = "";
  const row = document.createElement("tr");
  const cell = document.createElement("td");
  cell.colSpan = 3;
  cell.className = "empty-row";
  cell.textContent = text;
  row.appendChild(cell);
  alternativesBody.appendChild(row);
}

function resetPredictionResults(text = DEFAULT_RESULTS_MESSAGE) {
  predictionSummaryText.textContent = text;
  plainExplanationText.textContent = text;
  analystExplanation.textContent = text;
  evidenceNarrative.textContent = text;
  summaryPills.innerHTML = "";
  renderAlternativesEmpty(text);
  resultCount.textContent = "0";
  topScore.textContent = "N/A";
  setReviewChip("N/A", "neutral");
}

function renderEvidenceNarrative(text, spans) {
  if (!text) {
    evidenceNarrative.textContent = DEFAULT_RESULTS_MESSAGE;
    return;
  }
  if (!Array.isArray(spans) || !spans.length) {
    evidenceNarrative.textContent = text;
    return;
  }

  const sorted = spans
    .filter((span) => Number.isInteger(span.start) && Number.isInteger(span.end) && span.start < span.end)
    .sort((a, b) => a.start - b.start);

  let cursor = 0;
  let html = "";
  for (const span of sorted) {
    const start = Math.max(0, span.start);
    const end = Math.min(text.length, span.end);
    if (start < cursor) continue;
    html += escapeHtml(text.slice(cursor, start));
    const cls =
      span.importance === "high"
        ? "evidence-high"
        : span.importance === "medium"
          ? "evidence-medium"
          : "evidence-low";
    html += `<span class="evidence-highlight ${cls}">${escapeHtml(text.slice(start, end))}</span>`;
    cursor = end;
  }
  html += escapeHtml(text.slice(cursor));
  evidenceNarrative.innerHTML = html;
}

function formatPct(value) {
  return `${(Number(value) * 100).toFixed(1)}%`;
}

function renderSummaryPills(items) {
  summaryPills.innerHTML = "";
  items.forEach((text) => {
    const pill = document.createElement("span");
    pill.className = "pill";
    pill.textContent = text;
    summaryPills.appendChild(pill);
  });
}

function renderAnalystEvidenceTags(evidenceTerms) {
  if (!Array.isArray(evidenceTerms) || !evidenceTerms.length) {
    return "<p class='muted'>No evidence terms were extracted for this label.</p>";
  }
  const tags = evidenceTerms
    .map((item) => {
      const importance = item.importance || "low";
      const contribution = Number(item.contribution || 0).toFixed(4);
      const term = escapeHtml(item.display_term || item.term || "");
      return `<span class="evidence-tag ${importance}"><strong>${term}</strong><span>${importance}</span><span>${contribution}</span></span>`;
    })
    .join("");
  return `<div class="evidence-list">${tags}</div>`;
}

function renderAlternatives(rows) {
  if (!Array.isArray(rows) || !rows.length) {
    renderAlternativesEmpty(DEFAULT_RESULTS_MESSAGE);
    return;
  }
  alternativesBody.innerHTML = "";
  rows.forEach((item) => {
    const row = document.createElement("tr");
    const idCell = document.createElement("td");
    idCell.textContent = item.label_id || "N/A";
    const nameCell = document.createElement("td");
    nameCell.textContent = item.label_name || item.label_id || "N/A";
    const scoreCell = document.createElement("td");
    scoreCell.textContent = `${Number(item.score_percent || item.score * 100 || 0).toFixed(1)}%`;
    row.appendChild(idCell);
    row.appendChild(nameCell);
    row.appendChild(scoreCell);
    alternativesBody.appendChild(row);
  });
}

function renderPrediction(data, sourceText) {
  const predictedLabels = Array.isArray(data.predicted_labels) ? data.predicted_labels : [];
  const top = predictedLabels[0] || null;
  const summary = data.summary || {};

  resultCount.textContent = String(predictedLabels.length);
  topScore.textContent = top ? formatPct(top.score) : "N/A";

  if (!predictedLabels.length) {
    const noneMessage =
      "No root-cause-related factor indicators were above threshold for this narrative. Analyst review is recommended.";
    predictionSummaryText.textContent = noneMessage;
    plainExplanationText.textContent = noneMessage;
    analystExplanation.textContent = noneMessage;
    renderEvidenceNarrative(sourceText, []);
    renderSummaryPills([`Threshold ${Number(thresholdInput.value).toFixed(2)}`]);
    renderAlternatives(data.top_scores || []);
    setReviewChip("Review Recommended", "review");
    return;
  }

  const reviewFlag = Boolean(data.review_flag);
  setReviewChip(reviewFlag ? "Review Required" : "No Review Required", reviewFlag ? "review" : "ok");

  const labelName = top.label_name || top.label_id || top.label || "Unknown";
  const labelId = top.label_id || top.label || "Unknown";
  const summaryText = `${labelName} (${labelId}) is the leading indicator at ${formatPct(top.score)} confidence.`;
  predictionSummaryText.textContent = summaryText;

  plainExplanationText.textContent = top.plain_language_description
    ? `${top.plain_language_description} ${top.review_guidance || ""}`.trim()
    : "Plain-language explanation is not available for this label yet.";

  const analystText = [
    `<p><strong>${escapeHtml(labelName)}</strong> (${escapeHtml(labelId)})</p>`,
    `<p>${escapeHtml(top.technical_description || "Technical description unavailable.")}</p>`,
    `<p>${escapeHtml(top.operational_interpretation || "")}</p>`,
    `<p><strong>Confidence note:</strong> ${escapeHtml(top.confidence_note || "Analyst validation required.")}</p>`,
    `<p><strong>Explanation method:</strong> ${escapeHtml(top.explanation_method || data.model_info?.explanation_method || "unknown")}</p>`,
    renderAnalystEvidenceTags(top.evidence_terms || []),
  ].join("");
  analystExplanation.innerHTML = analystText;

  renderEvidenceNarrative(sourceText, top.evidence_spans || []);
  renderAlternatives((data.top_scores && data.top_scores.length ? data.top_scores : data.all_scores || []).slice(
    0,
    Number(topKInput.value),
  ));

  const threshold = Number(data.threshold_used || thresholdInput.value).toFixed(2);
  renderSummaryPills([
    `Domain ${data.domain || domainSelect.value}`,
    `Threshold ${threshold}`,
    `Top Score ${formatPct(top.score)}`,
    `Review ${reviewFlag ? "Required" : "Not required"}`,
    summary.top_label_name ? `Top Label ${summary.top_label_name}` : `Top Label ${labelName}`,
  ]);
}

function updateBatchStats(results) {
  const rows = results.length;
  const reviewCount = results.filter((item) => item.review_flag).length;
  const totalLabels = results.reduce((sum, item) => sum + (item.predicted_labels?.length || 0), 0);
  const avgLabels = rows ? totalLabels / rows : 0;
  batchRows.textContent = String(rows);
  batchReviewCount.textContent = String(reviewCount);
  batchAvgLabels.textContent = avgLabels.toFixed(2);
}

function renderEmptyBatchRow(text) {
  batchResultsBody.innerHTML = "";
  const row = document.createElement("tr");
  const cell = document.createElement("td");
  cell.colSpan = 5;
  cell.className = "empty-row";
  cell.textContent = text;
  row.appendChild(cell);
  batchResultsBody.appendChild(row);
}

function renderBatchPreview(results) {
  if (!results.length) {
    renderEmptyBatchRow(DEFAULT_BATCH_MESSAGE);
    return;
  }

  batchResultsBody.innerHTML = "";
  results.forEach((rowData) => {
    const row = document.createElement("tr");
    const rowIndex = document.createElement("td");
    rowIndex.textContent = String(rowData.row_index);

    const ids = document.createElement("td");
    ids.textContent = rowData.predicted_label_ids?.length
      ? rowData.predicted_label_ids.join(" | ")
      : rowData.predicted_labels?.map((x) => x.label_id || x.label || "N/A").join(" | ") ||
        "No labels above threshold";

    const names = document.createElement("td");
    names.textContent = rowData.predicted_label_names?.length
      ? rowData.predicted_label_names.join(" | ")
      : rowData.predicted_labels?.map((x) => x.label_name || x.label_id || x.label || "N/A").join(" | ") ||
        "No labels above threshold";

    const scores = document.createElement("td");
    scores.textContent =
      rowData.predicted_labels?.length
        ? rowData.predicted_labels.map((item) => `${(Number(item.score) * 100).toFixed(1)}%`).join(" | ")
        : "N/A";

    const review = document.createElement("td");
    const pill = document.createElement("span");
    pill.className = `review-pill ${rowData.review_flag ? "review-true" : "review-false"}`;
    pill.textContent = rowData.review_flag ? "Review Required" : "No Review Required";
    review.appendChild(pill);

    row.appendChild(rowIndex);
    row.appendChild(ids);
    row.appendChild(names);
    row.appendChild(scores);
    row.appendChild(review);
    batchResultsBody.appendChild(row);
  });
}

function normalizeErrorMessage(detail) {
  const raw = typeof detail === "string" ? detail : "Prediction request failed.";
  if (raw.toLowerCase().includes("artifact")) {
    return "Prediction is currently unavailable because the trained aviation model artifact is not loaded.";
  }
  if (raw.toLowerCase().includes("domain")) {
    return "The selected domain is not implemented for prediction.";
  }
  return raw;
}

function normalizeBatchError(detail) {
  const raw = typeof detail === "string" ? detail : "Batch prediction failed.";
  if (raw.toLowerCase().includes("csv must contain text column")) {
    return `Invalid CSV input. ${raw}`;
  }
  if (raw.toLowerCase().includes("utf-8")) {
    return "CSV must be UTF-8 encoded.";
  }
  if (raw.toLowerCase().includes("artifact")) {
    return "Batch prediction is unavailable because the trained aviation model artifact is not loaded.";
  }
  return raw;
}

async function loadDomains() {
  try {
    const res = await fetch("/domains");
    const payload = await res.json();
    domainSelect.innerHTML = "";
    payload.available_domains.forEach((item) => {
      const option = document.createElement("option");
      option.value = item.domain_id;
      option.textContent =
        item.status === "implemented"
          ? `${item.display_name} (implemented)`
          : `${item.display_name} (${item.status})`;
      if (item.status !== "implemented") option.disabled = true;
      if (item.domain_id === "aviation") option.selected = true;
      domainSelect.appendChild(option);
    });
  } catch (_err) {
    setBanner("Failed to load available domains. Check API availability.", "error");
    setReviewChip("Error", "error");
  }
}

async function runPrediction() {
  if (isPredicting) return;

  const narrative = narrativeInput.value.trim();
  if (!narrative) {
    const message = "Narrative text is required before scoring.";
    setBanner(message, "error");
    setPredictStatus(message, "warn");
    resetPredictionResults(DEFAULT_RESULTS_MESSAGE);
    return;
  }

  const payload = {
    text: narrative,
    domain: domainSelect.value,
    threshold: Number(thresholdInput.value),
    top_k: Number(topKInput.value),
  };

  setPredictLoading(true);
  setPredictStatus("Scoring narrative...", "warn");

  try {
    const res = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!res.ok) {
      const msg = normalizeErrorMessage(data.detail);
      setBanner(msg, "error");
      setPredictStatus(msg, "error");
      resetPredictionResults(DEFAULT_RESULTS_MESSAGE);
      setReviewChip("Unavailable", "error");
      return;
    }

    renderPrediction(data, narrative);
    const tone = data.review_flag ? "review" : "ok";
    setBanner(data.message || "Predictions generated successfully.", tone);
    setPredictStatus(
      data.review_flag
        ? "Scoring completed. Analyst review is recommended."
        : "Scoring completed. Review outputs with operational context.",
      data.review_flag ? "warn" : "success",
    );
  } catch (_err) {
    const msg = "Prediction request failed. Confirm the API is running.";
    setBanner(msg, "error");
    setPredictStatus(msg, "error");
    resetPredictionResults(DEFAULT_RESULTS_MESSAGE);
    setReviewChip("Unavailable", "error");
  } finally {
    setPredictLoading(false);
  }
}

function downloadCsv(filename, rows) {
  const csv = rows.join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

function buildBatchCsvRows(results) {
  const header = [
    "row_index",
    "input_text",
    "predicted_label_ids",
    "predicted_label_names",
    "scores",
    "review_flag",
    "message",
  ];
  const rows = [header.join(",")];

  results.forEach((row) => {
    const labelIds = (row.predicted_label_ids || row.predicted_labels?.map((x) => x.label_id || x.label) || []).join("|");
    const labelNames = (row.predicted_label_names || row.predicted_labels?.map((x) => x.label_name || x.label_id || x.label) || []).join("|");
    const scores = (row.predicted_labels || []).map((x) => x.score).join("|");
    const safeText = (row.input_text || "").replace(/"/g, '""');
    const safeMessage = (row.message || "").replace(/"/g, '""');
    rows.push(
      [
        row.row_index,
        `"${safeText}"`,
        `"${labelIds}"`,
        `"${labelNames}"`,
        `"${scores}"`,
        row.review_flag,
        `"${safeMessage}"`,
      ].join(","),
    );
  });
  return rows;
}

async function runBatch() {
  if (isBatchRunning) return;

  if (!batchFile.files.length) {
    setBatchStatus("Select a UTF-8 CSV file before running batch scoring.", "warn");
    return;
  }

  const textColumn = textColumnInput.value.trim() || "text";
  const formData = new FormData();
  formData.append("file", batchFile.files[0]);
  formData.append("domain", domainSelect.value);
  formData.append("threshold", thresholdInput.value);
  formData.append("top_k", topKInput.value);
  formData.append("text_column", textColumn);

  setBatchLoading(true);
  setBatchStatus(`Scoring batch using text column '${textColumn}'...`, "warn");

  try {
    const res = await fetch("/predict-batch", { method: "POST", body: formData });
    const data = await res.json();
    if (!res.ok) {
      const msg = normalizeBatchError(data.detail);
      setBatchStatus(msg, "error");
      lastBatchResults = [];
      downloadBtn.disabled = true;
      updateBatchStats([]);
      renderBatchPreview([]);
      return;
    }

    lastBatchResults = data.results || [];
    setBatchStatus(
      `Processed ${data.row_count} rows for domain '${data.domain}'. Review flagged rows for analyst follow-up.`,
      "success",
    );
    downloadBtn.disabled = lastBatchResults.length === 0;
    updateBatchStats(lastBatchResults);
    renderBatchPreview(lastBatchResults);
  } catch (_err) {
    setBatchStatus(
      "Batch request failed. Confirm the API is running and the CSV includes the expected text column.",
      "error",
    );
    lastBatchResults = [];
    downloadBtn.disabled = true;
    updateBatchStats([]);
    renderBatchPreview([]);
  } finally {
    setBatchLoading(false);
  }
}

function formatMetricValue(value) {
  if (typeof value === "number") {
    return Number.isInteger(value) ? String(value) : value.toFixed(3);
  }
  return value ?? "N/A";
}

async function loadModelInfo() {
  try {
    const res = await fetch("/model-info");
    const data = await res.json();
    modelInfo.innerHTML = "";
    const artifactStatus = data.artifact_status === "available" ? "available" : "missing";
    setArtifactBanner(artifactStatus);

    const items = [
      ["Model", data.model_name],
      ["Model Type", data.model_type],
      ["Domain", data.active_domain],
      ["Label Count", data.label_count],
      ["Threshold", data.threshold],
      ["Version", data.version],
      ["Training Date", data.training_date],
      ["Micro-F1", data.evaluation_metrics?.micro_f1],
      ["Macro-F1", data.evaluation_metrics?.macro_f1],
      ["Samples-F1", data.evaluation_metrics?.samples_f1],
      ["Hamming Loss", data.evaluation_metrics?.hamming_loss],
      ["Artifact Status", artifactStatus],
      ["Training Approach", data.training_approach],
      ["Dataset Note", data.dataset_provenance_note],
      ["Limitation", data.limitation_note],
    ];

    items.forEach(([key, value]) => {
      const item = document.createElement("div");
      item.className = "item";
      const keyEl = document.createElement("div");
      keyEl.className = "key";
      keyEl.textContent = key;
      const valueEl = document.createElement("div");
      valueEl.className = "value";
      valueEl.textContent = String(formatMetricValue(value));
      item.appendChild(keyEl);
      item.appendChild(valueEl);
      modelInfo.appendChild(item);
    });
  } catch (_err) {
    artifactBanner.classList.remove("hidden", "ok", "review", "error", "info");
    artifactBanner.classList.add("error");
    artifactBanner.textContent = "Unable to load model metadata. Check API connectivity for artifact status.";
    modelInfo.innerHTML = "<div class='item'>Unable to load model info.</div>";
  }
}

function applyDemoMode() {
  if (!demoMode) return;
  narrativeInput.value =
    "During approach, the crew received conflicting altitude instructions and descended below the assigned altitude before correcting after ATC communication.";
  thresholdInput.value = "0.5";
  thresholdValue.textContent = "0.50";
  topKInput.value = "5";
}

function initFeedbackPlaceholder() {
  feedbackButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const type = button.dataset.feedback || "feedback";
      const text = type.replaceAll("_", " ");
      feedbackStatus.textContent =
        `Feedback noted: ${text}. Feedback capture will be enabled in a future analyst-review workflow.`;
      feedbackStatus.classList.remove("error");
      feedbackStatus.classList.add("success");
    });
  });
}

predictBtn.addEventListener("click", runPrediction);
batchBtn.addEventListener("click", runBatch);
downloadBtn.addEventListener("click", () => {
  if (!lastBatchResults.length) return;
  const rows = buildBatchCsvRows(lastBatchResults);
  downloadCsv("batch_predictions.csv", rows);
});

async function init() {
  initTheme();
  initResultView();
  initFeedbackPlaceholder();
  resetPredictionResults(DEFAULT_RESULTS_MESSAGE);
  setPredictStatus("Ready for narrative scoring.");
  updateBatchStats([]);
  renderBatchPreview([]);
  applyDemoMode();
  await loadDomains();
  await loadModelInfo();
}

init();
