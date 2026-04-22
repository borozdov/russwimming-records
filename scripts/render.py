#!/usr/bin/env python3
"""Generate public/records.png and public/records.pdf from data/russia.json.

PNG  – beautiful A3-landscape table image via Pillow
PDF  – proper multi-page A4-landscape document via ReportLab (real selectable text)
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT   = Path(__file__).resolve().parent.parent
DATA   = ROOT / "data" / "russia.json"
PUBLIC = ROOT / "public"
FONTS  = ROOT / "static" / "fonts"

FONT_REG  = FONTS / "InterVariable.ttf"
FONT_BOLD = FONTS / "InterVariable.ttf"   # variable font covers bold via weight axis

# ── palette ──────────────────────────────────────────────────────────────────
BLUE_DARK   = (0,  45, 110)
BLUE_MID    = (0,  87, 184)
BLUE_LIGHT  = (0, 152, 212)
WHITE       = (255, 255, 255)
BG          = (237, 242, 249)
STRIPE_EVEN = (246, 249, 255)
STRIPE_ODD  = (255, 255, 255)
TEXT_DARK   = (13,  27,  42)
TEXT_MID    = (74,  96, 112)
TEXT_SUB    = (143, 163, 177)
GOLD_BG     = (255, 243, 205)
GOLD_FG     = (179,  89,   0)
PILL_BG     = (220, 234, 250)
PILL_FG     = (0,   87, 184)
FRESH_C     = (0,  135,  90)
RELAY_C     = (101, 84, 192)
SEPARATOR   = (228, 236, 246)


def hex_to_rl(r, g, b):
    return colors.Color(r / 255, g / 255, b / 255)


def load_data() -> dict:
    return json.loads(DATA.read_text(encoding="utf-8"))


# ─────────────────────────────────────────────────────────────────────────────
# PNG
# ─────────────────────────────────────────────────────────────────────────────

def _pil_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_BOLD if bold else FONT_REG
    return ImageFont.truetype(str(path), size)


def _draw_rect(draw: ImageDraw.Draw, xy, fill, radius=0):
    x0, y0, x1, y1 = xy
    if radius:
        draw.rounded_rectangle(xy, radius=radius, fill=fill)
    else:
        draw.rectangle(xy, fill=fill)


def _gradient_rect(img: Image.Image, x0, y0, x1, y1, c_left, c_right):
    """Horizontal linear gradient via numpy-free pixel fill."""
    w = x1 - x0
    for i in range(w):
        t = i / max(w - 1, 1)
        r = int(c_left[0] + (c_right[0] - c_left[0]) * t)
        g = int(c_left[1] + (c_right[1] - c_left[1]) * t)
        b = int(c_left[2] + (c_right[2] - c_left[2]) * t)
        draw = ImageDraw.Draw(img)
        draw.line([(x0 + i, y0), (x0 + i, y1)], fill=(r, g, b))


def _text_w(draw: ImageDraw.Draw, text: str, font) -> int:
    bb = draw.textbbox((0, 0), text, font=font)
    return bb[2] - bb[0]


def generate_png(data: dict, out: Path) -> None:
    DPR     = 2
    PW      = 2400          # logical pixels
    PAD     = 64
    HEADER  = 220
    COL_H   = 48
    ROW_H   = 60
    FOOTER  = 80

    SITE_URL = "russwimming-records.borozdov.ru"

    # collect all records with category label
    all_records: list[dict] = []
    for cat in data["categories"]:
        for r in cat["records"]:
            all_records.append({**r, "_cat": cat["title"]})

    cols = [
        {"label": "Дисциплина",  "key": "discipline",  "w": 380, "align": "left"},
        {"label": "Категория",   "key": "_cat",         "w": 220, "align": "left"},
        {"label": "Спортсмен",   "key": "athlete",      "w": 340, "align": "left"},
        {"label": "Результат",   "key": "result",       "w": 160, "align": "right"},
        {"label": "Место",       "key": "location",     "w": 220, "align": "left"},
        {"label": "Дата",        "key": "date_original","w": 130, "align": "right"},
    ]
    table_w = sum(c["w"] for c in cols)
    assert table_w <= PW - PAD * 2, "cols too wide"

    body_h = COL_H + ROW_H * len(all_records)
    PH     = HEADER + 20 + body_h + 20 + FOOTER

    img  = Image.new("RGB", (PW * DPR, PH * DPR), BG)
    draw = ImageDraw.Draw(img)

    def sc(v): return v * DPR  # scale coordinate

    # ── header gradient ───────────────────────────────────────
    _gradient_rect(img, 0, 0, PW * DPR, HEADER * DPR, BLUE_DARK, BLUE_LIGHT)

    # decorative blobs
    blob_draw = ImageDraw.Draw(img)
    for bx, by, br, ba in [
        (PW - 80, -50, 200, 30),
        (PW - 260, 20, 130, 18),
        (PW + 30, 140, 160, 22),
    ]:
        blob_draw.ellipse(
            [sc(bx - br), sc(by - br), sc(bx + br), sc(by + br)],
            fill=(255, 255, 255, ba),
        )

    # left accent bar
    draw.rectangle([sc(PAD), sc(36), sc(PAD + 4), sc(140)],
                   fill=(255, 255, 255, 100))

    # eyebrow
    f_eye  = _pil_font(22, bold=True)
    draw.text((sc(PAD + 16), sc(40)), "РЕКОРДЫ ПЛАВАНИЯ  ·  РОССИЯ",
              font=f_eye, fill=(255, 255, 255, 160))

    # title
    f_title = _pil_font(58, bold=True)
    draw.text((sc(PAD + 16), sc(70)), "Рекорды России по плаванию",
              font=f_title, fill=WHITE)

    # pills
    f_pill = _pil_font(22, bold=True)
    pill_y = HEADER - 64
    pill_x = PAD + 16
    for pill_text in [f"{len(all_records)} рекордов",
                      data["fetched_at"][:10]]:
        tw = _text_w(draw, pill_text, f_pill)
        pw2, ph2, pr2 = tw + 32, 38, 19
        draw.rounded_rectangle(
            [sc(pill_x), sc(pill_y), sc(pill_x + pw2), sc(pill_y + ph2)],
            radius=sc(pr2),
            fill=(255, 255, 255, 40),
        )
        draw.text((sc(pill_x + 16), sc(pill_y + 9)), pill_text,
                  font=f_pill, fill=WHITE)
        pill_x += pw2 + 10

    # site url top-right
    f_url = _pil_font(20)
    uw = _text_w(draw, SITE_URL, f_url)
    draw.text((sc(PW - PAD - uw), sc(42)), SITE_URL,
              font=f_url, fill=(255, 255, 255, 110))

    # ── table card ────────────────────────────────────────────
    card_y = HEADER + 20
    card_h = body_h
    card_x = PAD
    card_w = table_w

    # shadow (fake with slightly offset darker rect)
    draw.rounded_rectangle(
        [sc(card_x + 3), sc(card_y + 6), sc(card_x + card_w + 3), sc(card_y + card_h + 6)],
        radius=sc(14), fill=(180, 200, 220, 60),
    )
    draw.rounded_rectangle(
        [sc(card_x), sc(card_y), sc(card_x + card_w), sc(card_y + card_h)],
        radius=sc(14), fill=WHITE,
    )

    # column header bg gradient
    _gradient_rect(img, sc(card_x), sc(card_y), sc(card_x + card_w), sc(card_y + COL_H),
                   (0, 63, 150), (0, 134, 195))

    # column header text
    f_col = _pil_font(21, bold=True)
    cx = card_x + 16
    for col in cols:
        label = col["label"].upper()
        if col["align"] == "right":
            lw = _text_w(draw, label, f_col)
            draw.text((sc(cx + col["w"] - lw - 8), sc(card_y + 13)),
                      label, font=f_col, fill=(255, 255, 255, 220))
        else:
            draw.text((sc(cx + 4), sc(card_y + 13)), label,
                      font=f_col, fill=(255, 255, 255, 220))
        cx += col["w"]

    # rows
    f_main = _pil_font(24, bold=True)
    f_sub  = _pil_font(20)
    f_mono = _pil_font(26, bold=True)
    f_loc  = _pil_font(22)

    from datetime import date as _date
    one_year_ago = _date.today().replace(year=_date.today().year - 1).isoformat()

    for i, rec in enumerate(all_records):
        ry = card_y + COL_H + i * ROW_H
        stripe = STRIPE_EVEN if i % 2 == 0 else STRIPE_ODD
        draw.rectangle([sc(card_x), sc(ry), sc(card_x + card_w), sc(ry + ROW_H)],
                       fill=stripe)

        # separator
        if i > 0:
            draw.line([sc(card_x + 12), sc(ry), sc(card_x + card_w - 12), sc(ry)],
                      fill=SEPARATOR, width=DPR)

        # left accent
        is_fresh = bool(rec.get("date") and rec["date"] >= one_year_ago)
        if rec.get("relay"):
            draw.rectangle([sc(card_x), sc(ry + 10), sc(card_x + 5), sc(ry + ROW_H - 10)],
                           fill=RELAY_C)
        elif is_fresh:
            draw.rectangle([sc(card_x), sc(ry + 10), sc(card_x + 5), sc(ry + ROW_H - 10)],
                           fill=FRESH_C)

        cx = card_x + 16
        mid_y = ry + ROW_H // 2

        col_vals = [
            rec.get("discipline", ""),
            rec.get("_cat", ""),
            rec.get("athlete", ""),
            rec.get("result", ""),
            rec.get("location", ""),
            rec.get("date_original", ""),
        ]

        for ci, (col, val) in enumerate(zip(cols, col_vals)):
            val = str(val or "")
            max_w = col["w"] - 20

            if ci == 3:  # Result — pill
                is_best = i == 0
                bg_pill = GOLD_BG if is_best else PILL_BG
                fg_pill = GOLD_FG if is_best else PILL_FG
                vw = _text_w(draw, val, f_mono)
                pill_w, pill_h = vw + 28, 40
                pill_x2 = cx + col["w"] - pill_w - 8
                pill_y2 = mid_y - pill_h // 2
                draw.rounded_rectangle(
                    [sc(pill_x2), sc(pill_y2), sc(pill_x2 + pill_w), sc(pill_y2 + pill_h)],
                    radius=sc(8), fill=bg_pill,
                )
                draw.text((sc(pill_x2 + 14), sc(pill_y2 + 7)), val,
                          font=f_mono, fill=fg_pill)
            elif col["align"] == "right":
                vw = _text_w(draw, val, f_loc)
                draw.text((sc(cx + col["w"] - vw - 8), sc(mid_y - 12)), val,
                          font=f_loc, fill=TEXT_MID)
            else:
                # truncate if too wide
                font_used = f_main if ci == 0 else (f_sub if ci == 1 else f_loc)
                while val and _text_w(draw, val + "…", font_used) > sc(max_w):
                    val = val[:-1]
                if len(val) < len(str(col_vals[ci] or "")):
                    val += "…"
                ty = mid_y - 14 if ci == 0 else mid_y - 12
                fc = TEXT_DARK if ci in (0, 2) else TEXT_MID
                draw.text((sc(cx + (8 if ci == 0 else 2)), sc(ty)), val,
                          font=font_used, fill=fc)

            cx += col["w"]

    # round clip the card bottom (overdraw corners)
    # just re-draw background over corner artifacts
    draw.rounded_rectangle(
        [sc(card_x), sc(card_y), sc(card_x + card_w), sc(card_y + card_h)],
        radius=sc(14), outline=BG, width=DPR * 2,
    )

    # ── footer ────────────────────────────────────────────────
    foot_y = PH - FOOTER
    draw.line([sc(PAD), sc(foot_y + 8), sc(PAD + table_w), sc(foot_y + 8)],
              fill=SEPARATOR, width=DPR)

    f_foot_b = _pil_font(24, bold=True)
    f_foot   = _pil_font(22)
    draw.text((sc(PAD), sc(foot_y + 16)), f"🏊  {SITE_URL}",
              font=f_foot_b, fill=BLUE_MID)
    draw.text((sc(PAD), sc(foot_y + 44)), "Данные: russwimming.ru · обновляется раз в сутки",
              font=f_foot, fill=TEXT_SUB)

    # legend right
    for lc, lt in [(FRESH_C, "новый рекорд"), (RELAY_C, "эстафета")]:
        tw2 = _text_w(draw, lt, f_foot)
        rx = PW - PAD - tw2 - 30
        draw.text((sc(rx + 22), sc(foot_y + 44)), lt, font=f_foot, fill=TEXT_SUB)
        draw.ellipse([sc(rx + 4), sc(foot_y + 50), sc(rx + 18), sc(foot_y + 64)],
                     fill=lc)

    # export at 144 dpi
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(out), "PNG", dpi=(144, 144), optimize=True)
    print(f"  PNG → {out.relative_to(ROOT)}  ({img.width}×{img.height}px)")


# ─────────────────────────────────────────────────────────────────────────────
# PDF
# ─────────────────────────────────────────────────────────────────────────────

def generate_pdf(data: dict, out: Path) -> None:
    pdfmetrics.registerFont(TTFont("Inter", str(FONT_REG)))
    pdfmetrics.registerFont(TTFont("Inter-Bold", str(FONT_BOLD)))

    PAGE = landscape(A4)
    pw, ph = PAGE

    doc = SimpleDocTemplate(
        str(out),
        pagesize=PAGE,
        leftMargin=14 * mm, rightMargin=14 * mm,
        topMargin=12 * mm,  bottomMargin=12 * mm,
    )

    C = colors
    accent    = hex_to_rl(*BLUE_MID)
    accent_dk = hex_to_rl(*BLUE_DARK)
    gold_bg   = hex_to_rl(*GOLD_BG)
    gold_fg   = hex_to_rl(*GOLD_FG)
    pill_bg   = hex_to_rl(*PILL_BG)
    pill_fg   = hex_to_rl(*PILL_FG)
    fresh_c   = hex_to_rl(*FRESH_C)
    relay_c   = hex_to_rl(*RELAY_C)
    sep_c     = hex_to_rl(*SEPARATOR)
    bg_even   = hex_to_rl(*STRIPE_EVEN)
    text_mid  = hex_to_rl(*TEXT_MID)
    text_sub  = hex_to_rl(*TEXT_SUB)
    white     = C.white

    body_style = ParagraphStyle("body", fontName="Inter", fontSize=8, leading=10,
                                 textColor=hex_to_rl(*TEXT_DARK))
    sub_style  = ParagraphStyle("sub",  fontName="Inter", fontSize=7, leading=9,
                                 textColor=hex_to_rl(*TEXT_MID))
    bold_style = ParagraphStyle("bold", fontName="Inter-Bold", fontSize=8.5, leading=10,
                                 textColor=hex_to_rl(*TEXT_DARK))
    result_style = ParagraphStyle("res", fontName="Inter-Bold", fontSize=9, leading=11,
                                   textColor=pill_fg, alignment=2)  # right

    from datetime import date as _date
    one_year_ago = _date.today().replace(year=_date.today().year - 1).isoformat()

    story = []

    for cat in data["categories"]:
        # ── category header ──────────────────────────────────
        header_data = [[
            Paragraph(
                f'<font color="white"><b>{cat["title"]}</b></font>  '
                f'<font color="#aaccee" size="7">{len(cat["records"])} рекордов</font>',
                ParagraphStyle("hdr", fontName="Inter-Bold", fontSize=11,
                               textColor=white, leading=14),
            )
        ]]
        header_tbl = Table(header_data, colWidths=[pw - 28 * mm])
        header_tbl.setStyle(TableStyle([
            ("BACKGROUND",  (0, 0), (-1, -1), accent),
            ("LEFTPADDING",  (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING",   (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
            ("ROUNDEDCORNERS", [6]),
        ]))
        story.append(header_tbl)
        story.append(Spacer(1, 3 * mm))

        # ── column headers ───────────────────────────────────
        col_header = ParagraphStyle("ch", fontName="Inter-Bold", fontSize=7.5,
                                    textColor=white, leading=9)
        ch_row = [
            Paragraph("ДИСЦИПЛИНА",  col_header),
            Paragraph("СПОРТСМЕН",   col_header),
            Paragraph("РЕЗУЛЬТАТ",   ParagraphStyle("chr", fontName="Inter-Bold",
                                     fontSize=7.5, textColor=white, leading=9, alignment=2)),
            Paragraph("МЕСТО",       col_header),
            Paragraph("ДАТА",        ParagraphStyle("chd", fontName="Inter-Bold",
                                     fontSize=7.5, textColor=white, leading=9, alignment=2)),
        ]
        col_w = [pw * 0.26, pw * 0.27, pw * 0.12, pw * 0.20, pw * 0.09]
        col_w = [c - 28 * mm / len(col_w) for c in col_w]

        rows = [ch_row]
        styles = [
            ("BACKGROUND",   (0, 0), (-1, 0), accent_dk),
            ("TEXTCOLOR",    (0, 0), (-1, 0), white),
            ("FONTNAME",     (0, 0), (-1, 0), "Inter-Bold"),
            ("FONTSIZE",     (0, 0), (-1, 0), 7.5),
            ("TOPPADDING",   (0, 0), (-1, 0), 6),
            ("BOTTOMPADDING",(0, 0), (-1, 0), 6),
            ("LEFTPADDING",  (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [bg_even, white]),
            ("LINEBELOW",    (0, 0), (-1, -1), 0.4, sep_c),
            ("FONTNAME",     (0, 1), (-1, -1), "Inter"),
            ("FONTSIZE",     (0, 1), (-1, -1), 8),
        ]

        for i, rec in enumerate(cat["records"]):
            discipline = Paragraph(rec.get("discipline", ""), bold_style)

            athlete_text = rec.get("athlete", "")
            if rec.get("roster"):
                roster = ", ".join(rec["roster"])
                athlete_text += f'<br/><font color="#8fa3b1" size="7"><i>{roster}</i></font>'
            athlete = Paragraph(athlete_text, body_style)

            result_val = rec.get("result", "")
            is_best = i == 0
            res_bg  = gold_bg if is_best else pill_bg
            res_fg  = gold_fg if is_best else pill_fg
            result  = Paragraph(
                f'<b>{result_val}</b>',
                ParagraphStyle("rr", fontName="Inter-Bold", fontSize=9, leading=11,
                               textColor=res_fg, alignment=2),
            )

            location = Paragraph(rec.get("location", ""), sub_style)
            date_val = Paragraph(
                rec.get("date_original", ""),
                ParagraphStyle("dr", fontName="Inter", fontSize=7.5, leading=9,
                               textColor=hex_to_rl(*TEXT_MID), alignment=2),
            )

            rows.append([discipline, athlete, result, location, date_val])

            # color result cell background
            row_idx = i + 1
            styles.append(("BACKGROUND", (2, row_idx), (2, row_idx), res_bg))

            # accent left border for fresh/relay
            is_fresh = bool(rec.get("date") and rec["date"] >= one_year_ago)
            if rec.get("relay"):
                styles.append(("LINEAFTER",  (-1, row_idx), (-1, row_idx), 0, white))
                styles.append(("LINEBEFORE", (0, row_idx), (0, row_idx), 3, relay_c))
            elif is_fresh:
                styles.append(("LINEBEFORE", (0, row_idx), (0, row_idx), 3, fresh_c))

        tbl = Table(rows, colWidths=col_w, repeatRows=1)
        tbl.setStyle(TableStyle(styles))
        story.append(tbl)
        story.append(Spacer(1, 6 * mm))

    # footer on each page
    SITE_URL = "russwimming-records.borozdov.ru"
    fetched  = data["fetched_at"][:10]

    def on_page(canvas_obj, doc_obj):
        canvas_obj.saveState()
        canvas_obj.setFont("Inter", 7)
        canvas_obj.setFillColor(text_sub)
        canvas_obj.drawString(14 * mm, 7 * mm,
                              f"🏊 {SITE_URL}  ·  Источник: russwimming.ru  ·  Обновлено: {fetched}")
        canvas_obj.drawRightString(pw - 14 * mm, 7 * mm,
                                   f"Стр. {doc_obj.page}")
        canvas_obj.restoreState()

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    print(f"  PDF → {out.relative_to(ROOT)}")


def main():
    data = load_data()
    print("Rendering exports…")
    generate_png(data, PUBLIC / "records.png")
    generate_pdf(data, PUBLIC / "records.pdf")
    print("Done.")


if __name__ == "__main__":
    main()
