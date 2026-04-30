const domainSelect = document.getElementById("domainSelect");
const thresholdInput = document.getElementById("thresholdInput");
const thresholdValue = document.getElementById("thresholdValue");
const topKInput = document.getElementById("topKInput");
const narrativeInput = document.getElementById("narrativeInput");
const predictBtn = document.getElementById("predictBtn");
const resultsBody = document.getElementById("resultsBody");
const reviewBanner = document.getElementById("reviewBanner");
const resultCount = document.getElementById("resultCount");
const topScore = document.getElementById("topScore");
const reviewFlagChip = document.getElementById("reviewFlagChip");
const reviewFlagValue = document.getElementById("reviewFlagValue");
const modelInfo = document.getElementById("modelInfo");

const batchFile = document.getElementById("batchFile");
const batchBtn = document.getElementById("batchBtn");
const downloadBtn = document.getElementById("downloadBtn");
const batchStatus = document.getElementById("batchStatus");
const textColumnInput = document.getElementById("textColumnInput");
const batchRows = document.getElementById("batchRows");
const batchAvgLabels = document.getElementById("batchAvgLabels");
const batchReviewCount = document.getElementById("batchReviewCount");
const batchResultsBody = document.getElementById("batchResultsBody");

let lastBatchResults = [];
const urlParams = new URLSearchParams(window.location.search);
const demoMode = (urlParams.get("demo") || "").toLowerCase();
const viewMode = (urlParams.get("view") || "").toLowerCase();

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

function setBanner(text, tone) {
  reviewBanner.classList.remove("hidden", "ok", "review", "error");
  reviewBanner.classList.add(tone);
  reviewBanner.textContent = text;
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

function setBatchStatus(text, tone = "") {
  batchStatus.classList.remove("success", "warn", "error");
  if (tone) {
    batchStatus.classList.add(tone);
  }
  batchStatus.textContent = text;
}

function renderEmptyResultsRow(text, colspan = 3) {
  resultsBody.innerHTML = `<tr><td colspan="${colspan}" class="empty-row">${text}</td></tr>`;
}

function renderEmptyBatchRow(text) {
  batchResultsBody.innerHTML = `<tr><td colspan="4" class="empty-row">${text}</td></tr>`;
}

function updateBatchStats(results) {
  const rows = results.length;
  const reviewCount = results.filter((item) => item.review_flag).length;
  const totalLabels = results.reduce(
    (sum, item) => sum + (item.predicted_labels?.length || 0),
    0,
  );
  const avgLabels = rows ? totalLabels / rows : 0;

  batchRows.textContent = String(rows);
  batchReviewCount.textContent = String(reviewCount);
  batchAvgLabels.textContent = avgLabels.toFixed(2);
}

function renderBatchPreview(results) {
  if (!results.length) {
    renderEmptyBatchRow("No batch results yet. Upload a CSV and run batch prediction.");
    return;
  }

  batchResultsBody.innerHTML = "";
  results.forEach((row) => {
    const labels = row.predicted_labels?.map((item) => item.label).join(" | ") || "None";
    const scores =
      row.predicted_labels
        ?.map((item) => Number(item.score).toFixed(2))
        .join(" | ") || "N/A";
    const reviewClass = row.review_flag ? "review-true" : "review-false";
    const reviewText = row.review_flag ? "True" : "False";

    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${row.row_index}</td>
      <td>${labels}</td>
      <td>${scores}</td>
      <td><span class="review-pill ${reviewClass}">${reviewText}</span></td>
    `;
    batchResultsBody.appendChild(tr);
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
    renderEmptyResultsRow("No labels above threshold.");
    resultCount.textContent = "0";
    topScore.textContent = "N/A";
    return;
  }

  resultCount.textContent = String(predictedLabels.length);
  const maxScore = Math.max(...predictedLabels.map((item) => item.score));
  topScore.textContent = `${(maxScore * 100).toFixed(1)}%`;

  predictedLabels.forEach((item) => {
    const confidencePct = (item.score * 100).toFixed(1);
    const confidenceClass =
      item.score >= 0.75
        ? "confidence-high"
        : item.score >= 0.55
          ? "confidence-medium"
          : "confidence-low";
    const cues = (item.explanation_terms || [])
      .map((term) => `<span class="cue-tag">${term}</span>`)
      .join("");
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${item.label}</td>
      <td><span class="confidence-badge ${confidenceClass}">${confidencePct}%</span></td>
      <td>${cues || "<span class='muted'>No cues available</span>"}</td>
    `;
    resultsBody.appendChild(row);
  });
}

async function runPrediction() {
  const narrative = narrativeInput.value.trim();
  if (!narrative) {
    setBanner("Narrative text is required before prediction.", "error");
    renderResults([]);
    return;
  }

  const payload = {
    text: narrative,
    domain: domainSelect.value,
    threshold: Number(thresholdInput.value),
    top_k: Number(topKInput.value),
  };

  try {
    const res = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json();
    if (!res.ok) {
      setBanner(data.detail || "Prediction failed.", "error");
      renderResults([]);
      setReviewChip("Error", "error");
      return;
    }

    renderResults(data.predicted_labels);
    const tone = data.review_flag ? "review" : "ok";
    setBanner(data.message, tone);
    setReviewChip(data.review_flag ? "True" : "False", tone);
  } catch (_err) {
    setBanner("Request failed. Confirm the API server is running.", "error");
    renderResults([]);
    setReviewChip("Error", "error");
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
    "predicted_labels",
    "scores",
    "review_flag",
    "message",
  ];
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

async function runBatch() {
  if (!batchFile.files.length) {
    setBatchStatus("Please choose a CSV file first.", "warn");
    return;
  }

  const formData = new FormData();
  formData.append("file", batchFile.files[0]);
  formData.append("domain", domainSelect.value);
  formData.append("threshold", thresholdInput.value);
  formData.append("top_k", topKInput.value);
  formData.append("text_column", textColumnInput.value.trim() || "text");

  try {
    const res = await fetch("/predict-batch", {
      method: "POST",
      body: formData,
    });
    const data = await res.json();

    if (!res.ok) {
      setBatchStatus(data.detail || "Batch prediction failed.", "error");
      downloadBtn.disabled = true;
      lastBatchResults = [];
      updateBatchStats([]);
      renderBatchPreview([]);
      return;
    }

    lastBatchResults = data.results || [];
    setBatchStatus(`Processed ${data.row_count} rows for domain '${data.domain}'.`, "success");
    downloadBtn.disabled = lastBatchResults.length === 0;
    updateBatchStats(lastBatchResults);
    renderBatchPreview(lastBatchResults);
  } catch (_err) {
    setBatchStatus("Batch request failed. Confirm the API server is running.", "error");
    downloadBtn.disabled = true;
    lastBatchResults = [];
    updateBatchStats([]);
    renderBatchPreview([]);
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
      ["Artifact Status", data.artifact_status],
      ["Training Approach", data.training_approach],
      ["Dataset Note", data.dataset_provenance_note],
      ["Limitation", data.limitation_note],
    ];

    items.forEach(([key, value]) => {
      const item = document.createElement("div");
      item.className = "item";
      item.innerHTML = `<div class="key">${key}</div><div class="value">${formatMetricValue(value)}</div>`;
      modelInfo.appendChild(item);
    });
  } catch (_err) {
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
    {
      label: "Anomaly_4",
      score: 0.54,
      explanation_terms: ["workload", "handoff", "sequencing"],
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
      predicted_labels: [
        { label: "Anomaly_7", score: 0.58 },
        { label: "Anomaly_4", score: 0.54 },
      ],
      review_flag: false,
      message: "Predictions generated successfully.",
    },
    {
      row_index: 2,
      input_text: "Sample row 2",
      predicted_labels: [
        { label: "Anomaly_11", score: 0.61 },
        { label: "Anomaly_5", score: 0.57 },
      ],
      review_flag: true,
      message: "Low-confidence profile. Analyst review recommended.",
    },
    {
      row_index: 3,
      input_text: "Sample row 3",
      predicted_labels: [
        { label: "Anomaly_2", score: 0.79 },
        { label: "Anomaly_7", score: 0.55 },
      ],
      review_flag: false,
      message: "Predictions generated successfully.",
    },
  ];
}

function applyDemoMode() {
  if (!demoMode) {
    return;
  }

  narrativeInput.value =
    "Crew received conflicting altitude and approach instructions during descent in busy terminal airspace.";
  thresholdInput.value = "0.5";
  thresholdValue.textContent = "0.50";
  topKInput.value = "5";

  if (demoMode === "prediction" || demoMode === "batch") {
    renderResults(samplePrediction());
    setBanner("Predictions generated successfully.", "ok");
    setReviewChip("False", "ok");
  }

  if (demoMode === "batch") {
    lastBatchResults = sampleBatch();
    updateBatchStats(lastBatchResults);
    renderBatchPreview(lastBatchResults);
    setBatchStatus("Processed 4 rows for domain 'aviation'.", "success");
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
  setViewMode();
  setReviewChip("N/A", "neutral");
  updateBatchStats([]);
  renderBatchPreview([]);
  await loadDomains();
  await loadModelInfo();
  applyDemoMode();
}

init();
