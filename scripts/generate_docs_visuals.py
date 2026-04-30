"""Generate polished README visuals for docs/images."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

WIDTH = 1600
HEIGHT = 900
BG = "#f3f7fc"
PANEL = "#ffffff"
BORDER = "#c8d5e6"
TEXT = "#213047"
MUTED = "#5a6f8c"
ARROW = "#4f6484"


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    base = "/usr/share/fonts/truetype/dejavu"
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(f"{base}/{name}", size=size)


F_TITLE = _font(46, bold=True)
F_SUBTITLE = _font(30)
F_CARD_TITLE = _font(28, bold=True)
F_CARD_BODY = _font(24)
F_FLOW_TITLE = _font(20, bold=True)
F_FLOW_BODY = _font(17)
F_SMALL = _font(22)
F_TINY = _font(20)


def _canvas() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    return img, ImageDraw.Draw(img)


def _header(draw: ImageDraw.ImageDraw, title: str, subtitle: str) -> None:
    draw.rounded_rectangle(
        (30, 24, WIDTH - 30, 124),
        radius=18,
        fill="#e8eff8",
        outline=BORDER,
        width=2,
    )
    draw.text((60, 45), title, font=F_TITLE, fill=TEXT)
    draw.text((60, 93), subtitle, font=F_SMALL, fill=MUTED)


def _card(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int, int, int],
    title: str,
    body: str,
    *,
    fill: str = PANEL,
    border: str = BORDER,
    title_color: str = TEXT,
    body_color: str = MUTED,
    title_font: ImageFont.FreeTypeFont = F_CARD_TITLE,
    body_font: ImageFont.FreeTypeFont = F_CARD_BODY,
) -> None:
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle((x0, y0, x1, y1), radius=14, fill=fill, outline=border, width=2)
    title_bottom = _draw_multiline(
        draw,
        title,
        (x0 + 18, y0 + 20),
        x1 - x0 - 34,
        title_font,
        title_color,
        line_gap=4,
    )
    _draw_multiline(
        draw,
        body,
        (x0 + 18, title_bottom + 6),
        x1 - x0 - 34,
        body_font,
        body_color,
        line_gap=5,
    )


def _draw_multiline(
    draw: ImageDraw.ImageDraw,
    text: str,
    pos: tuple[int, int],
    max_width: int,
    font: ImageFont.FreeTypeFont,
    fill: str,
    line_gap: int = 8,
) -> int:
    x, y = pos
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            y += font.size + line_gap
            continue
        line: list[str] = []
        for word in words:
            test = " ".join(line + [word])
            w = draw.textlength(test, font=font)
            if w <= max_width:
                line.append(word)
                continue
            if line:
                draw.text((x, y), " ".join(line), font=font, fill=fill)
                y += font.size + line_gap
            line = [word]
        if line:
            draw.text((x, y), " ".join(line), font=font, fill=fill)
            y += font.size + line_gap
    return y


def _arrow(
    draw: ImageDraw.ImageDraw,
    start: tuple[int, int],
    end: tuple[int, int],
    *,
    color: str = ARROW,
    width: int = 6,
    head_len: int = 16,
) -> None:
    draw.line((start, end), fill=color, width=width)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    p1 = (
        end[0] - head_len * math.cos(angle - math.pi / 6),
        end[1] - head_len * math.sin(angle - math.pi / 6),
    )
    p2 = (
        end[0] - head_len * math.cos(angle + math.pi / 6),
        end[1] - head_len * math.sin(angle + math.pi / 6),
    )
    draw.polygon([end, p1, p2], fill=color)


def make_architecture(path: Path) -> None:
    img, draw = _canvas()
    _header(
        draw,
        "Architecture - Operations RCA NLP",
        "Clear service flow from user interaction to analyst-facing outputs",
    )

    y0, y1 = 230, 500
    gap = 24
    widths = [170, 170, 180, 190, 280, 190, 190]
    titles = [
        "User / Analyst",
        "Web UI",
        "FastAPI API",
        "Domain Registry",
        "Prediction / Explanation / Batch Services",
        "Model Artifacts",
        "Analyst Outputs",
    ]
    bodies = [
        "Submits incident narratives and reviews outputs.",
        "Single and batch workflows with threshold and top-k controls.",
        "Routes: /health, /domains, /model-info, /predict, /predict-batch.",
        "Domain metadata and implementation status registry.",
        "Prediction scoring, cue extraction, and batch CSV processing.",
        "Model joblib, metadata, and label mapping files.",
        "Factor labels, confidence scores, cue terms, and review flags.",
    ]
    fills = ["#f9fbff", "#eff6ff", "#eff8ff", "#eefbff", "#f2f7ff", "#f6faff", "#eefaf3"]
    borders = ["#b8c9e0", "#90b5e4", "#8eb9e8", "#97c3da", "#9fb8e3", "#afc6e6", "#98d1ad"]

    x = 38
    boxes: list[tuple[int, int, int, int]] = []
    for w, title, body, fill, border in zip(widths, titles, bodies, fills, borders):
        box = (x, y0, x + w, y1)
        boxes.append(box)
        _card(
            draw,
            box,
            title,
            body,
            fill=fill,
            border=border,
            body_color="#405671",
            title_font=F_FLOW_TITLE,
            body_font=F_FLOW_BODY,
        )
        x += w + gap

    center_y = (y0 + y1) // 2
    for i in range(len(boxes) - 1):
        _arrow(
            draw,
            (boxes[i][2] + 4, center_y),
            (boxes[i + 1][0] - 8, center_y),
        )

    draw.rounded_rectangle(
        (110, 620, WIDTH - 110, 812),
        radius=14,
        fill="#ffffff",
        outline=BORDER,
        width=2,
    )
    draw.text((138, 652), "Flow Summary", font=F_CARD_TITLE, fill=TEXT)
    _draw_multiline(
        draw,
        (
            "User/Analyst -> Web UI -> FastAPI API -> Domain Registry -> "
            "Prediction/Explanation/Batch Services -> Model Artifacts -> Analyst Outputs"
        ),
        (138, 704),
        WIDTH - 276,
        F_SUBTITLE,
        "#334a68",
        line_gap=10,
    )
    img.save(path)


def make_model_workflow(path: Path) -> None:
    img, draw = _canvas()
    _header(
        draw,
        "Model Workflow - Inference Pipeline",
        "Narrative text transformed into reviewable factor indicators",
    )

    step_titles = [
        "Incident Narrative",
        "Text Preprocessing",
        "TF-IDF Features",
        "Multi-label Logistic Regression",
        "Factor Scores",
        "Threshold Filtering",
        "Review Flag",
        "Structured Output",
    ]
    step_bodies = [
        "Raw report text",
        "Clean, normalize, tokenize",
        "Sparse weighted vectors",
        "One-vs-rest scoring",
        "Per-label probabilities",
        "Keep labels above threshold",
        "Escalate uncertain cases",
        "Labels, confidence, cues",
    ]
    fills = [
        "#eef6ff",
        "#edf9ff",
        "#eefcf8",
        "#f3f5ff",
        "#f4f7ff",
        "#fff8ed",
        "#fff4ee",
        "#eefbf3",
    ]
    borders = [
        "#9ec2eb",
        "#9fd2e6",
        "#a8d8c3",
        "#b9b9ef",
        "#b9c8e8",
        "#ecc386",
        "#e7b9a5",
        "#9fd2ad",
    ]

    y0, y1 = 260, 470
    w, gap = 170, 18
    x = 57
    boxes: list[tuple[int, int, int, int]] = []
    for title, body, fill, border in zip(step_titles, step_bodies, fills, borders):
        box = (x, y0, x + w, y1)
        boxes.append(box)
        _card(
            draw,
            box,
            title,
            body,
            fill=fill,
            border=border,
            body_color="#3f536d",
            title_font=F_FLOW_TITLE,
            body_font=F_FLOW_BODY,
        )
        x += w + gap

    mid_y = (y0 + y1) // 2
    for i in range(len(boxes) - 1):
        _arrow(draw, (boxes[i][2] + 3, mid_y), (boxes[i + 1][0] - 6, mid_y))

    draw.rounded_rectangle(
        (120, 560, WIDTH - 120, 804),
        radius=14,
        fill="#ffffff",
        outline=BORDER,
        width=2,
    )
    draw.text((152, 596), "Output Semantics", font=F_CARD_TITLE, fill=TEXT)
    _draw_multiline(
        draw,
        (
            "Predictions are root-cause-related contributory-factor indicators for analyst review. "
            "They are confidence-ranked and review-flagged outputs, not definitive causal determination."
        ),
        (152, 648),
        WIDTH - 300,
        F_SUBTITLE,
        "#3b526f",
        line_gap=10,
    )
    img.save(path)


def make_metrics(path: Path) -> None:
    img, draw = _canvas()
    _header(
        draw,
        "Metrics Summary - Aviation Demonstration",
        "Current baseline snapshot for 22-label multi-label classification",
    )

    draw.rounded_rectangle((90, 180, 980, 760), radius=16, fill="#ffffff", outline=BORDER, width=2)
    draw.text((130, 220), "F1 Scores", font=F_CARD_TITLE, fill=TEXT)

    labels = ["Micro-F1", "Macro-F1", "Samples-F1"]
    values = [0.658, 0.630, 0.654]
    colors = ["#1b7f77", "#2f65d4", "#6f42d8"]
    base_x = 130
    y_top = 640
    chart_h = 330
    bar_w = 170
    gap = 90

    draw.line((base_x, y_top, 930, y_top), fill="#98aac4", width=4)
    draw.line((base_x, y_top, base_x, y_top - chart_h), fill="#98aac4", width=4)

    for idx, (label, value, color) in enumerate(zip(labels, values, colors)):
        x0 = base_x + 90 + idx * (bar_w + gap)
        x1 = x0 + bar_w
        y1 = y_top
        y0 = int(y_top - chart_h * value)
        draw.rounded_rectangle((x0, y0, x1, y1), radius=10, fill=color)
        val = f"{value:.3f}"
        tw = draw.textlength(val, font=F_CARD_TITLE)
        draw.text((x0 + (bar_w - tw) / 2, y0 - 46), val, font=F_CARD_TITLE, fill=TEXT)
        lw = draw.textlength(label, font=F_CARD_BODY)
        draw.text((x0 + (bar_w - lw) / 2, y_top + 28), label, font=F_CARD_BODY, fill="#334963")

    for tick in [0.2, 0.4, 0.6, 0.8, 1.0]:
        y = int(y_top - chart_h * tick)
        draw.line((base_x, y, 930, y), fill="#e3ebf5", width=2)
        draw.text((base_x - 48, y - 12), f"{tick:.1f}", font=F_TINY, fill="#6c809b")

    draw.rounded_rectangle((1040, 230, 1490, 640), radius=16, fill="#fff7ef", outline="#e8c495", width=2)
    draw.text((1080, 280), "Hamming Loss", font=F_CARD_TITLE, fill="#85410a")
    draw.text((1080, 360), "0.073", font=_font(64, bold=True), fill="#162238")
    _draw_multiline(
        draw,
        "Lower is better. Indicates low per-label error in this aviation demo baseline.",
        (1080, 470),
        360,
        F_SUBTITLE,
        "#7e4318",
        line_gap=12,
    )

    draw.rounded_rectangle((90, 790, WIDTH - 90, 850), radius=12, fill="#ffffff", outline=BORDER, width=2)
    draw.text(
        (120, 808),
        "Metrics: Micro-F1 0.658 | Macro-F1 0.630 | Samples-F1 0.654 | Hamming Loss 0.073",
        font=F_TINY,
        fill="#415978",
    )
    img.save(path)


def _pill(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int, int, int],
    text: str,
    *,
    fill: str,
    border: str,
    ink: str,
) -> None:
    draw.rounded_rectangle(xy, radius=18, fill=fill, outline=border, width=2)
    tw = draw.textlength(text, font=F_TINY)
    x0, y0, x1, y1 = xy
    draw.text((x0 + (x1 - x0 - tw) / 2, y0 + 8), text, font=F_TINY, fill=ink)


def make_prediction_result(path: Path) -> None:
    img, draw = _canvas()
    _header(
        draw,
        "Prediction Result View",
        "Single narrative scoring output with confidence and explanation cues",
    )

    draw.rounded_rectangle((70, 170, WIDTH - 70, 300), radius=14, fill="#ffffff", outline=BORDER, width=2)
    draw.text((100, 200), "Incident Narrative", font=F_CARD_TITLE, fill=TEXT)
    _draw_multiline(
        draw,
        "Crew received conflicting altitude and approach instructions during descent in busy terminal airspace.",
        (100, 242),
        WIDTH - 220,
        F_CARD_BODY,
        "#334a66",
    )

    draw.rounded_rectangle((70, 330, WIDTH - 70, 392), radius=12, fill="#eaf7ef", outline="#a5d7b8", width=2)
    draw.text(
        (98, 348),
        "Review Flag: FALSE   |   Message: Predictions generated successfully.",
        font=F_TINY,
        fill="#1d6a40",
    )

    draw.rounded_rectangle((70, 420, WIDTH - 70, 820), radius=14, fill="#ffffff", outline=BORDER, width=2)
    draw.text((100, 452), "Predicted Factor Labels", font=F_CARD_TITLE, fill=TEXT)

    x0, y0, x1 = 100, 500, WIDTH - 100
    header_h = 52
    draw.rounded_rectangle((x0, y0, x1, y0 + header_h), radius=8, fill="#edf3fb", outline="#bfd0e6", width=2)
    draw.text((124, y0 + 14), "Label", font=F_TINY, fill="#2e435f")
    draw.text((420, y0 + 14), "Confidence", font=F_TINY, fill="#2e435f")
    draw.text((640, y0 + 14), "Explanation Cues", font=F_TINY, fill="#2e435f")

    rows = [
        ("Anomaly_2", "0.81", "altitude, approach, clearance"),
        ("Anomaly_19", "0.64", "communication, controller, instruction"),
        ("Anomaly_7", "0.58", "descent, deviation, conflict"),
        ("Anomaly_4", "0.54", "workload, sequencing, handoff"),
    ]
    y = y0 + header_h + 14
    for label, score, cues in rows:
        draw.rounded_rectangle((x0, y, x1, y + 64), radius=8, fill="#f9fbff", outline="#d2deed", width=2)
        draw.text((124, y + 18), label, font=F_CARD_BODY, fill=TEXT)
        _pill(draw, (392, y + 12, 500, y + 52), score, fill="#e9f0ff", border="#b7c8e8", ink="#204cb5")
        draw.text((640, y + 18), cues, font=F_CARD_BODY, fill="#4a5f7b")
        y += 78

    img.save(path)


def make_batch_scoring(path: Path) -> None:
    img, draw = _canvas()
    _header(
        draw,
        "Batch Scoring View",
        "CSV upload workflow with structured multi-row prediction output",
    )

    draw.rounded_rectangle((70, 170, WIDTH - 70, 390), radius=14, fill="#ffffff", outline=BORDER, width=2)
    draw.text((100, 200), "Batch Input Controls", font=F_CARD_TITLE, fill=TEXT)

    draw.rounded_rectangle((100, 248, 620, 306), radius=10, fill="#f7faff", outline="#c5d4e8", width=2)
    draw.text((122, 267), "CSV file: aviation_batch_reports.csv", font=F_TINY, fill="#475d7a")

    draw.rounded_rectangle((650, 248, 960, 306), radius=10, fill="#f7faff", outline="#c5d4e8", width=2)
    draw.text((672, 267), "Text column: text", font=F_TINY, fill="#475d7a")

    draw.rounded_rectangle((990, 248, 1185, 306), radius=10, fill="#1b7f77", outline="#15685f", width=2)
    draw.text((1038, 267), "Run Batch", font=F_TINY, fill="#ffffff")

    draw.rounded_rectangle((1210, 248, 1450, 306), radius=10, fill="#2f65d4", outline="#2a57b4", width=2)
    draw.text((1242, 267), "Download CSV", font=F_TINY, fill="#ffffff")

    stats = [("Rows Processed", "48"), ("Avg Labels / Row", "2.3"), ("Review Flags", "6")]
    sx = 100
    for name, value in stats:
        draw.rounded_rectangle((sx, 326, sx + 240, 374), radius=10, fill="#eef5ff", outline="#bfd0e6", width=2)
        draw.text((sx + 16, 338), f"{name}: {value}", font=F_TINY, fill="#324a68")
        sx += 260

    draw.rounded_rectangle((70, 420, WIDTH - 70, 820), radius=14, fill="#ffffff", outline=BORDER, width=2)
    draw.text((100, 452), "Batch Output Preview", font=F_CARD_TITLE, fill=TEXT)

    x0, y0, x1 = 100, 502, WIDTH - 100
    draw.rounded_rectangle((x0, y0, x1, y0 + 52), radius=8, fill="#edf3fb", outline="#bfd0e6", width=2)
    columns = ["row_index", "predicted_labels", "scores", "review_flag"]
    col_x = [118, 280, 830, 1200]
    for col, cx in zip(columns, col_x):
        draw.text((cx, y0 + 15), col, font=F_TINY, fill="#2e435f")

    rows = [
        ("0", "Anomaly_2|Anomaly_19", "0.81|0.64", "False"),
        ("1", "Anomaly_7|Anomaly_4", "0.58|0.54", "False"),
        ("2", "Anomaly_11|Anomaly_5", "0.61|0.57", "True"),
        ("3", "Anomaly_2|Anomaly_7", "0.79|0.55", "False"),
    ]
    y = y0 + 66
    for ridx, labels, scores, flag in rows:
        draw.rounded_rectangle((x0, y, x1, y + 60), radius=8, fill="#f9fbff", outline="#d2deed", width=2)
        draw.text((124, y + 17), ridx, font=F_CARD_BODY, fill="#3c516d")
        draw.text((280, y + 17), labels, font=F_CARD_BODY, fill="#3c516d")
        draw.text((830, y + 17), scores, font=F_CARD_BODY, fill="#3c516d")
        flag_fill = "#eaf7ef" if flag == "False" else "#fff4e6"
        flag_border = "#a5d7b8" if flag == "False" else "#f0c98f"
        flag_ink = "#1d6a40" if flag == "False" else "#8a4c05"
        _pill(draw, (1180, y + 10, 1310, y + 50), flag, fill=flag_fill, border=flag_border, ink=flag_ink)
        y += 74

    img.save(path)


def main() -> None:
    out_dir = Path(__file__).resolve().parents[1] / "docs" / "images"
    out_dir.mkdir(parents=True, exist_ok=True)
    make_architecture(out_dir / "architecture.png")
    make_model_workflow(out_dir / "model_workflow.png")
    make_metrics(out_dir / "metrics_summary.png")
    print(f"Generated visuals in {out_dir}")


if __name__ == "__main__":
    main()
