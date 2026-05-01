const domainSelect = document.getElementById("domainSelect");
const thresholdInput = document.getElementById("thresholdInput");
const thresholdValue = document.getElementById("thresholdValue");
const topKInput = document.getElementById("topKInput");
const narrativeInput = document.getElementById("narrativeInput");
const predictBtn = document.getElementById("predictBtn");
const predictStatus = document.getElementById("predictStatus");
const resultsBody = document.getElementById("resultsBody");
const reviewBanner = document.getElementById("reviewBanner");
const resultCount = document.getElementById("resultCount");
const topScore = document.getElementById("topScore");
const reviewFlagChip = document.getElementById("reviewFlagChip");
const reviewFlagValue = document.getElementById("reviewFlagValue");
const modelInfo = document.getElementById("modelInfo");
const artifactBanner = document.getElementById("artifactBanner");
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

const THEME_STORAGE_KEY = "orca_nlp_theme_mode";
const DEFAULT_RESULTS_MESSAGE = "No prediction results yet. Enter a narrative and run scoring.";
const DEFAULT_BATCH_MESSAGE = "No batch results yet. Upload a CSV and run batch prediction.";
const themeMediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
let selectedThemeMode = "system";
let lastBatchResults = [];
let isPredicting = false;
let isBatchRunning = false;

const urlParams = new URLSearchParams(window.location.search);
const demoMode = (urlParams.get("demo") || "").toLowerCase();
const viewMode = (urlParams.get("view") || "").toLowerCase();
const forcedThemeMode = (urlParams.get("theme") || "").toLowerCase();

thresholdInput.addEventListener("input", () => {
  thresholdValue.textContent = Number(thresholdInput.value).toFixed(2);
});

function setViewMode() {
  if (viewMode === "prediction") {
    document.body.classList.add("view-prediction");
  } else if (viewMode === "batch") {
    document.body.classList.add("view-batch");
  }
}

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
  if (forcedThemeMode === "light" || forcedThemeMode === "dark" || forcedThemeMode === "system") {
    mode = forcedThemeMode;
  } else {
    try {
      const saved = localStorage.getItem(THEME_STORAGE_KEY);
      mode = saved === "light" || saved === "dark" || saved === "system" ? saved : "system";
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
      // Ignore storage errors and keep in-memory theme mode.
    }
    applyTheme(next);
  });

  themeMediaQuery.addEventListener("change", () => {
    if (selectedThemeMode === "system") {
      applyTheme("system");
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
  if (tone) {
    predictStatus.classList.add(tone);
  }
  predictStatus.textContent = text;
}

function setBatchStatus(text, tone = "") {
  batchStatus.classList.remove("success", "warn", "error");
  if (tone) {
    batchStatus.classList.add(tone);
  }
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

function renderEmptyResultsRow(text) {
  resultsBody.innerHTML = "";
  const row = document.createElement("tr");
  const cell = document.createElement("td");
  cell.colSpan = 3;
  cell.className = "empty-row";
  cell.textContent = text;
  row.appendChild(cell);
  resultsBody.appendChild(row);
}

function renderEmptyBatchRow(text) {
  batchResultsBody.innerHTML = "";
  const row = document.createElement("tr");
  const cell = document.createElement("td");
  cell.colSpan = 4;
  cell.className = "empty-row";
  cell.textContent = text;
  row.appendChild(cell);
  batchResultsBody.appendChild(row);
}

function resetPredictionResults(text = DEFAULT_RESULTS_MESSAGE) {
  renderEmptyResultsRow(text);
  resultCount.textContent = "0";
  topScore.textContent = "N/A";
  setReviewChip("N/A", "neutral");
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

    const labels = document.createElement("td");
    labels.textContent =
      rowData.predicted_labels?.length
        ? rowData.predicted_labels.map((item) => item.label).join(" | ")
        : "No labels above threshold";

    const scores = document.createElement("td");
    scores.textContent =
      rowData.predicted_labels?.length
        ? rowData.predicted_labels
            .map((item) => `${(Number(item.score) * 100).toFixed(1)}%`)
            .join(" | ")
        : "N/A";

    const reviewFlag = document.createElement("td");
    const reviewPill = document.createElement("span");
    reviewPill.className = `review-pill ${rowData.review_flag ? "review-true" : "review-false"}`;
    reviewPill.textContent = rowData.review_flag ? "Review Required" : "No Review Required";
    reviewFlag.appendChild(reviewPill);

    row.appendChild(rowIndex);
    row.appendChild(labels);
    row.appendChild(scores);
    row.appendChild(reviewFlag);
    batchResultsBody.appendChild(row);
  });
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

function renderResults(predictedLabels) {
  resultsBody.innerHTML = "";
  if (!predictedLabels.length) {
    renderEmptyResultsRow(
      "No root-cause-related factor indicators were above threshold for this narrative. Analyst review is recommended.",
    );
    resultCount.textContent = "0";
    topScore.textContent = "N/A";
    setReviewChip("Review Recommended", "review");
    return;
  }

  resultCount.textContent = String(predictedLabels.length);
  const maxScore = Math.max(...predictedLabels.map((item) => Number(item.score)));
  topScore.textContent = `${(maxScore * 100).toFixed(1)}%`;

  predictedLabels.forEach((item) => {
    const score = Number(item.score);
    const confidencePct = `${(score * 100).toFixed(1)}%`;
    const confidenceClass =
      score >= 0.75 ? "confidence-high" : score >= 0.55 ? "confidence-medium" : "confidence-low";
    const row = document.createElement("tr");

    const labelCell = document.createElement("td");
    labelCell.textContent = item.label;

    const confidenceCell = document.createElement("td");
    const confidenceBadge = document.createElement("span");
    confidenceBadge.className = `confidence-badge ${confidenceClass}`;
    confidenceBadge.textContent = confidencePct;
    confidenceCell.appendChild(confidenceBadge);

    const cuesCell = document.createElement("td");
    if (Array.isArray(item.explanation_terms) && item.explanation_terms.length) {
      item.explanation_terms.forEach((term) => {
        const cue = document.createElement("span");
        cue.className = "cue-tag";
        cue.textContent = term;
        cuesCell.appendChild(cue);
      });
    } else {
      const noCues = document.createElement("span");
      noCues.className = "muted";
      noCues.textContent = "No explanation cues available";
      cuesCell.appendChild(noCues);
    }

    row.appendChild(labelCell);
    row.appendChild(confidenceCell);
    row.appendChild(cuesCell);
    resultsBody.appendChild(row);
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

async function runPrediction() {
  if (isPredicting) return;

  const narrative = narrativeInput.value.trim();
  if (!narrative) {
    const textRequiredMessage = "Narrative text is required before scoring.";
    setBanner(textRequiredMessage, "error");
    setPredictStatus(textRequiredMessage, "warn");
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

    renderResults(data.predicted_labels || []);
    const tone = data.review_flag ? "review" : "ok";
    setBanner(data.message || "Scoring completed.", tone);
    setPredictStatus(
      data.review_flag
        ? "Scoring completed. Analyst review is recommended."
        : "Scoring completed. Review outputs with operational context.",
      data.review_flag ? "warn" : "success",
    );
    setReviewChip(data.review_flag ? "Review Required" : "No Review Required", tone);
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
  const header = ["row_index", "input_text", "predicted_labels", "scores", "review_flag", "message"];
  const rows = [header.join(",")];

  results.forEach((row) => {
    const labels = row.predicted_labels.map((x) => x.label).join("|");
    const scores = row.predicted_labels.map((x) => x.score).join("|");
    const safeText = (row.input_text || "").replace(/"/g, '""');
    const safeMessage = (row.message || "").replace(/"/g, '""');
    rows.push(
      [
        row.row_index,
        `"${safeText}"`,
        `"${labels}"`,
        `"${scores}"`,
        row.review_flag,
        `"${safeMessage}"`,
      ].join(","),
    );
  });
  return rows;
}

function normalizeBatchError(detail) {
  const raw = typeof detail === "string" ? detail : "Batch prediction failed.";
  if (raw.toLowerCase().includes("csv must contain text column")) {
    return `Invalid CSV input. ${raw} Check the text-column field and upload again.`;
  }
  if (raw.toLowerCase().includes("utf-8")) {
    return "CSV must be UTF-8 encoded.";
  }
  if (raw.toLowerCase().includes("artifact")) {
    return "Batch prediction is unavailable because the trained aviation model artifact is not loaded.";
  }
  return raw;
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
      downloadBtn.disabled = true;
      lastBatchResults = [];
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
    downloadBtn.disabled = true;
    lastBatchResults = [];
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
    artifactBanner.textContent =
      "Unable to load model metadata. Check API connectivity for artifact status.";
    modelInfo.innerHTML = "<div class='item'>Unable to load model info.</div>";
  }
}

function samplePrediction() {
  return [
    {
      label: "Anomaly_2",
      score: 0.81,
      explanation_terms: ["altitude", "approach", "clearance"],
    },
    {
      label: "Anomaly_19",
      score: 0.64,
      explanation_terms: ["communication", "controller", "instruction"],
    },
    {
      label: "Anomaly_7",
      score: 0.58,
      explanation_terms: ["descent", "deviation", "conflict"],
    },
  ];
}

function sampleBatch() {
  return [
    {
      row_index: 0,
      input_text: "Sample row 0",
      predicted_labels: [
        { label: "Anomaly_2", score: 0.81 },
        { label: "Anomaly_19", score: 0.64 },
      ],
      review_flag: false,
      message: "Predictions generated successfully.",
    },
    {
      row_index: 1,
      input_text: "Sample row 1",
      predicted_labels: [{ label: "Anomaly_7", score: 0.58 }],
      review_flag: true,
      message: "Low-confidence assessment — manual review advised.",
    },
  ];
}

function applyDemoMode() {
  if (!demoMode) return;

  narrativeInput.value =
    "Crew received conflicting altitude and approach instructions during descent in busy terminal airspace.";
  thresholdInput.value = "0.5";
  thresholdValue.textContent = "0.50";
  topKInput.value = "5";

  if (demoMode === "prediction" || demoMode === "batch") {
    renderResults(samplePrediction());
    setBanner("Predictions generated successfully.", "ok");
    setReviewChip("No Review Required", "ok");
    setPredictStatus("Demo prediction loaded.", "success");
  }

  if (demoMode === "batch") {
    lastBatchResults = sampleBatch();
    updateBatchStats(lastBatchResults);
    renderBatchPreview(lastBatchResults);
    setBatchStatus("Processed 2 demo rows for domain 'aviation'.", "success");
    downloadBtn.disabled = false;
  }
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
  setViewMode();
  resetPredictionResults(DEFAULT_RESULTS_MESSAGE);
  setPredictStatus("Ready for narrative scoring.");
  updateBatchStats([]);
  renderBatchPreview([]);
  await loadDomains();
  await loadModelInfo();
  applyDemoMode();
}

init();
