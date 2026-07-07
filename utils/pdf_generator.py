"""
PDF generation for agreements — Ethiopian AI Supply Chain Platform
=========================================================
Fixes & New Features:
  - Fixed: generate_agreement_pdf() now accepts both `price` and `price_per_unit` kwargs
  - Fixed: forecast_demand() horizon parameter handled gracefully
  - Feature 1: Preview-ready HTML string alongside PDF bytes
  - Feature 2: Producer sends order + agreement on best match
  - Feature 3: Merchant confirms + downloads PDF
  - Feature 4: All user types can download the agreement PDF
  - Feature 5: Agreement auto-sent to merchant when order is placed
  - Feature 6: Full detailed agreement with all legal clauses
"""

import io
import datetime
import uuid
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# ── Agreement terms ──────────────────────────────────────────────────────────
AGREEMENT_TERMS = [
    ("Quality Assurance",
     "The Seller guarantees that all goods supplied conform to the grade and "
     "specifications stated in Section 2. Goods not meeting agreed quality "
     "standards may be returned at the Seller's expense within 48 hours of delivery."),

    ("Delivery Obligation",
     "The Seller shall deliver the goods to the agreed destination on or before "
     "the Delivery Date. A delay of more than 3 business days without written "
     "notice constitutes a material breach."),

    ("Payment Terms",
     "The Buyer shall remit payment in full via the agreed Payment Method within "
     "5 business days of confirmed delivery. Late payment attracts a penalty of "
     "1.5% per month on the outstanding balance."),

    ("Force Majeure",
     "Neither party shall be liable for delays or failures caused by natural "
     "disasters, government action, civil unrest, or other events beyond their "
     "reasonable control, provided the affected party gives written notice within "
     "72 hours of the event."),

    ("Dispute Resolution",
     "Any dispute arising from this Agreement shall first be resolved through "
     "good-faith negotiation. Failing resolution within 14 days, the matter "
     "shall be referred to the Ethiopian Trade Arbitration Centre."),

    ("Governing Law",
     "This Agreement is governed by the laws of the Federal Democratic Republic "
     "of Ethiopia, including the Commercial Code (Proclamation No. 1243/2021)."),

    ("Confidentiality",
     "Both parties agree to keep the terms of this Agreement and all related "
     "commercial information confidential and not to disclose them to third "
     "parties without prior written consent."),

    ("Amendment",
     "No amendment to this Agreement is valid unless made in writing and signed "
     "by authorised representatives of both parties."),

    ("Entire Agreement",
     "This document constitutes the entire agreement between the parties and "
     "supersedes all prior negotiations, representations, or arrangements, "
     "whether written or oral."),

    ("Platform Terms",
     "Both parties acknowledge that this transaction was facilitated by the "
     "Ethiopian AI Supply Chain Platform ('the Platform') and agree to abide by "
     "the Platform's Terms of Service and Code of Conduct."),
]


# ── Colour palette ────────────────────────────────────────────────────────────
GREEN_DARK  = colors.HexColor("#1B4332")
GREEN_MID   = colors.HexColor("#2D6A4F")
GREEN_LIGHT = colors.HexColor("#D8F3DC")
GOLD        = colors.HexColor("#F4A261")
GREY_LIGHT  = colors.HexColor("#F8F9FA")
GREY_TEXT   = colors.HexColor("#6C757D")
WHITE       = colors.white
BLACK       = colors.black


# ─────────────────────────────────────────────────────────────────────────────
# CORE PDF GENERATOR
# ─────────────────────────────────────────────────────────────────────────────

def generate_agreement_pdf(
    producer_name: str,
    producer_phone: str,
    producer_region: str,
    merchant_name: str,
    merchant_phone: str,
    merchant_region: str,
    product_name: str,
    sector: str,
    quality_grade: str,
    quantity: float,
    unit: str,
    # ── FIX: accept both `price` and `price_per_unit` from caller ──
    price_per_unit: float = None,
    price: float = None,                  # ← alias kept for backward compat
    total_price: float = None,
    delivery_date: str = "",
    payment_method: str = "Bank Transfer",
    notes: str = "",
    agreement_id: str = None,
    producer_confirmed: bool = False,
    merchant_confirmed: bool = False,
    delivery_location: str = "",
    producer_woreda: str = "",
    merchant_woreda: str = "",
) -> bytes:
    """
    Generate a full detailed agreement PDF and return raw bytes.

    Accepts `price` **or** `price_per_unit` interchangeably so existing
    callers that pass `price=...` keep working without modification.
    """
    # ── Resolve price alias ──────────────────────────────────────────────────
    if price_per_unit is None and price is not None:
        price_per_unit = price
    if price_per_unit is None:
        price_per_unit = 0.0
    if total_price is None:
        total_price = price_per_unit * quantity
    if agreement_id is None:
        agreement_id = str(uuid.uuid4())

    ref = f"AGR-{agreement_id[:8].upper()}"
    today = datetime.date.today().strftime("%d %B %Y")
    now   = datetime.datetime.now().strftime("%d %B %Y, %H:%M")

    # ── Status label ─────────────────────────────────────────────────────────
    if producer_confirmed and merchant_confirmed:
        status_text  = "FULLY EXECUTED"
        status_color = colors.HexColor("#2D6A4F")
    elif producer_confirmed:
        status_text  = "PENDING MERCHANT CONFIRMATION"
        status_color = GOLD
    else:
        status_text  = "DRAFT — AWAITING CONFIRMATION"
        status_color = GREY_TEXT

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm,  bottomMargin=2*cm,
    )

    base   = getSampleStyleSheet()
    title  = ParagraphStyle("T",  parent=base["Title"],
                            fontSize=20, textColor=GREEN_DARK,
                            alignment=TA_CENTER, spaceAfter=4)
    sub    = ParagraphStyle("S",  parent=base["Normal"],
                            fontSize=10, textColor=GREY_TEXT,
                            alignment=TA_CENTER, spaceAfter=2)
    sec    = ParagraphStyle("H",  parent=base["Heading2"],
                            fontSize=12, textColor=GREEN_DARK,
                            spaceBefore=14, spaceAfter=6,
                            borderPad=2)
    body   = ParagraphStyle("B",  parent=base["Normal"],
                            fontSize=10, leading=16, spaceAfter=4)
    small  = ParagraphStyle("Sm", parent=base["Normal"],
                            fontSize=8,  textColor=GREY_TEXT,
                            alignment=TA_CENTER)

    story = []

    # ── Header ───────────────────────────────────────────────────────────────
    story.append(Paragraph("🌾 Ethiopian AI Supply Chain Platform", sub))
    story.append(Paragraph("COMMERCIAL SUPPLY AGREEMENT", title))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=2, color=GREEN_DARK))
    story.append(Spacer(1, 6))

    # Meta table
    meta_data = [
        ["Reference", ref, "Date", today],
        ["Status", status_text, "Sector", sector],
    ]
    meta_table = Table(meta_data, colWidths=[3*cm, 7*cm, 3*cm, 5*cm])
    meta_table.setStyle(TableStyle([
        ("FONTNAME",  (0,0), (-1,-1), "Helvetica"),
        ("FONTSIZE",  (0,0), (-1,-1), 9),
        ("FONTNAME",  (0,0), (0,-1),  "Helvetica-Bold"),
        ("FONTNAME",  (2,0), (2,-1),  "Helvetica-Bold"),
        ("TEXTCOLOR", (1,1), (1,1),   status_color),
        ("FONTNAME",  (1,1), (1,1),   "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [GREY_LIGHT, WHITE]),
        ("GRID",      (0,0), (-1,-1), 0.3, GREY_TEXT),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 14))

    # ── Section 1: Parties ───────────────────────────────────────────────────
    story.append(Paragraph("1. PARTIES TO THIS AGREEMENT", sec))
    parties_data = [
        ["", "SELLER (Producer)", "BUYER (Merchant)"],
        ["Full Name",   producer_name,   merchant_name],
        ["Phone",       producer_phone,  merchant_phone],
        ["Region",      producer_region, merchant_region],
        ["Woreda/Zone", producer_woreda or "—", merchant_woreda or "—"],
        ["Confirmed",
         "✓ Yes" if producer_confirmed else "✗ Pending",
         "✓ Yes" if merchant_confirmed else "✗ Pending"],
    ]
    pt = Table(parties_data, colWidths=[4*cm, 8*cm, 8*cm])
    pt.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  GREEN_DARK),
        ("TEXTCOLOR",     (0,0), (-1,0),  WHITE),
        ("FONTNAME",      (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTNAME",      (0,1), (0,-1),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [GREY_LIGHT, WHITE]),
        ("GRID",          (0,0), (-1,-1), 0.3, GREY_TEXT),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("ALIGN",         (0,0), (-1,-1), "LEFT"),
        # colour confirmation row
        ("TEXTCOLOR",     (1,-1), (1,-1),
         GREEN_MID if producer_confirmed else GOLD),
        ("TEXTCOLOR",     (2,-1), (2,-1),
         GREEN_MID if merchant_confirmed else GOLD),
        ("FONTNAME",      (0,-1), (-1,-1), "Helvetica-Bold"),
    ]))
    story.append(pt)
    story.append(Spacer(1, 14))

    # ── Section 2: Goods & Commercial Terms ──────────────────────────────────
    story.append(Paragraph("2. GOODS AND COMMERCIAL TERMS", sec))
    goods_data = [
        ["Product Name",    product_name],
        ["Sector / Grade",  f"{sector}  —  Grade {quality_grade}"],
        ["Quantity",        f"{quantity:,.2f} {unit}"],
        ["Unit Price",      f"ETB {price_per_unit:,.2f} per {unit}"],
        ["Total Value",     f"ETB {total_price:,.2f}"],
        ["Delivery Date",   delivery_date or "To be confirmed"],
        ["Delivery Location", delivery_location or "To be confirmed"],
        ["Payment Method",  payment_method],
    ]
    if notes:
        goods_data.append(["Special Notes", notes])

    gt = Table(goods_data, colWidths=[5*cm, 13*cm])
    gt.setStyle(TableStyle([
        ("FONTNAME",   (0,0), (0,-1),  "Helvetica-Bold"),
        ("FONTSIZE",   (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [GREY_LIGHT, WHITE]),
        ("GRID",       (0,0), (-1,-1), 0.3, GREY_TEXT),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        # highlight total
        ("BACKGROUND", (0,4), (-1,4),  GREEN_LIGHT),
        ("FONTNAME",   (0,4), (-1,4),  "Helvetica-Bold"),
        ("TEXTCOLOR",  (1,4), (1,4),   GREEN_DARK),
    ]))
    story.append(gt)
    story.append(Spacer(1, 14))

    # ── Section 3: Terms & Conditions ────────────────────────────────────────
    story.append(Paragraph("3. TERMS AND CONDITIONS", sec))
    for i, (heading, text) in enumerate(AGREEMENT_TERMS, 1):
        story.append(Paragraph(
            f"<b>3.{i}  {heading}</b>",
            ParagraphStyle("tc_h", parent=body, textColor=GREEN_MID,
                           spaceBefore=8, spaceAfter=2)
        ))
        story.append(Paragraph(text, body))
    story.append(Spacer(1, 14))

    # ── Section 4: Obligations ────────────────────────────────────────────────
    story.append(Paragraph("4. SPECIFIC OBLIGATIONS", sec))
    obligations = [
        ("Producer / Seller shall:",
         ["Supply goods meeting agreed quality grade within the stated timeframe.",
          "Provide valid delivery documentation (invoice, weighbridge ticket).",
          "Notify the Buyer at least 24 hours before dispatch.",
          "Ensure goods are properly packaged to prevent damage in transit."]),
        ("Merchant / Buyer shall:",
         ["Arrange or confirm logistics for goods collection / delivery.",
          "Inspect goods at delivery point and sign delivery receipt.",
          "Remit full payment within the agreed payment window.",
          "Report any quality dispute within 48 hours of delivery."]),
    ]
    for role, duties in obligations:
        story.append(Paragraph(f"<b>{role}</b>", body))
        for d in duties:
            story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;• {d}", body))
    story.append(Spacer(1, 14))

    # ── Section 5: Confirmation & Signatures ─────────────────────────────────
    story.append(Paragraph("5. CONFIRMATION AND SIGNATURES", sec))
    story.append(Paragraph(
        "By signing below, both parties confirm that they have read, understood, "
        "and agree to be legally bound by all terms of this Agreement.", body
    ))
    story.append(Spacer(1, 20))

    sig_data = [
        ["SELLER (Producer)", "", "BUYER (Merchant)", ""],
        [f"Name: {producer_name}", "", f"Name: {merchant_name}", ""],
        ["Signature: ___________________________", "",
         "Signature: ___________________________", ""],
        [f"Date: {today}", "", f"Date: {today}", ""],
        ["Stamp / Seal: ___________________________", "",
         "Stamp / Seal: ___________________________", ""],
    ]
    sig_t = Table(sig_data, colWidths=[9*cm, 0.5*cm, 9*cm, 0.5*cm])
    sig_t.setStyle(TableStyle([
        ("FONTNAME",  (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",  (0,0), (-1,-1), 9),
        ("BACKGROUND",(0,0), (0,0),   GREEN_LIGHT),
        ("BACKGROUND",(2,0), (2,0),   GREEN_LIGHT),
        ("TOPPADDING",(0,0), (-1,-1), 7),
        ("BOTTOMPADDING",(0,0), (-1,-1), 7),
        ("LINEBELOW", (0,-1),(0,-1), 0.5, GREEN_DARK),
        ("LINEBELOW", (2,-1),(2,-1), 0.5, GREEN_DARK),
    ]))
    story.append(sig_t)
    story.append(Spacer(1, 20))

    # ── Footer ────────────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1, color=GREY_TEXT))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        f"Generated: {now}  |  Ref: {ref}  |  "
        "Ethiopian AI Supply Chain Platform  |  "
        "This document is legally binding upon confirmation by both parties.",
        small
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


# ─────────────────────────────────────────────────────────────────────────────
# AGREEMENT HTML PREVIEW  (Feature 1 & 3 — preview before PDF download)
# ─────────────────────────────────────────────────────────────────────────────

def generate_agreement_preview_html(
    producer_name, producer_phone, producer_region,
    merchant_name, merchant_phone, merchant_region,
    product_name, sector, quality_grade,
    quantity, unit,
    price_per_unit=None, price=None,
    total_price=None,
    delivery_date="", payment_method="Bank Transfer",
    notes="", agreement_id=None,
    producer_confirmed=False, merchant_confirmed=False,
    delivery_location="",
) -> str:
    """
    Return an HTML string for in-app agreement preview (read-only).
    The merchant sees this before confirming / downloading the PDF.
    """
    if price_per_unit is None:
        price_per_unit = price or 0.0
    if total_price is None:
        total_price = price_per_unit * quantity
    if agreement_id is None:
        agreement_id = str(uuid.uuid4())

    ref   = f"AGR-{agreement_id[:8].upper()}"
    today = datetime.date.today().strftime("%d %B %Y")

    status = ("✅ FULLY EXECUTED" if producer_confirmed and merchant_confirmed
              else "⏳ PENDING MERCHANT CONFIRMATION" if producer_confirmed
              else "📝 DRAFT")

    terms_html = "".join(
        f"<li><b>{h}:</b> {t}</li>" for h, t in AGREEMENT_TERMS
    )

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Agreement Preview — {ref}</title>
<style>
  body{{font-family:Arial,sans-serif;background:#0d1b2a;color:#e0e0e0;
       margin:0;padding:16px;font-size:14px;}}
  .card{{background:#1a2a3a;border-radius:10px;padding:20px;
         max-width:700px;margin:auto;box-shadow:0 4px 20px rgba(0,0,0,.4);}}
  h1{{color:#2D6A4F;font-size:18px;text-align:center;margin-bottom:4px;}}
  .sub{{text-align:center;color:#888;font-size:12px;margin-bottom:14px;}}
  .badge{{display:inline-block;padding:4px 12px;border-radius:20px;
          font-size:12px;font-weight:bold;margin-bottom:14px;
          background:{'#1B4332' if producer_confirmed and merchant_confirmed else '#4A3500'};
          color:{'#D8F3DC' if producer_confirmed and merchant_confirmed else '#F4A261'};}}
  table{{width:100%;border-collapse:collapse;margin-bottom:14px;}}
  th{{background:#1B4332;color:#fff;padding:8px;text-align:left;font-size:13px;}}
  td{{padding:7px 8px;border-bottom:1px solid #2a3a4a;font-size:13px;}}
  tr:nth-child(even) td{{background:#1e2d3d;}}
  .total td{{background:#1B4332 !important;color:#D8F3DC;font-weight:bold;}}
  h2{{color:#2D6A4F;font-size:15px;border-bottom:1px solid #2a3a4a;
      padding-bottom:4px;margin-top:20px;}}
  ol li{{margin-bottom:8px;line-height:1.5;}}
  .footer{{text-align:center;color:#555;font-size:11px;margin-top:20px;}}
  .sig-box{{display:flex;gap:20px;margin-top:14px;}}
  .sig{{flex:1;border:1px dashed #2D6A4F;border-radius:8px;padding:12px;}}
  .sig .name{{font-weight:bold;margin-bottom:8px;color:#D8F3DC;}}
  .sig-line{{border-bottom:1px solid #2D6A4F;margin:20px 0 6px;}}
  .confirmed{{color:#2D6A4F;font-weight:bold;}}
  .pending{{color:#F4A261;}}
</style>
</head>
<body>
<div class="card">
  <div class="sub">🌾 Ethiopian AI Supply Chain Platform</div>
  <h1>COMMERCIAL SUPPLY AGREEMENT</h1>
  <div class="sub">Ref: {ref} &nbsp;|&nbsp; Date: {today}</div>
  <div style="text-align:center"><span class="badge">{status}</span></div>

  <h2>1. Parties</h2>
  <table>
    <tr><th></th><th>SELLER (Producer)</th><th>BUYER (Merchant)</th></tr>
    <tr><td><b>Name</b></td><td>{producer_name}</td><td>{merchant_name}</td></tr>
    <tr><td><b>Phone</b></td><td>{producer_phone}</td><td>{merchant_phone}</td></tr>
    <tr><td><b>Region</b></td><td>{producer_region}</td><td>{merchant_region}</td></tr>
    <tr><td><b>Confirmed</b></td>
        <td class="{'confirmed' if producer_confirmed else 'pending'}">
          {'✓ Yes' if producer_confirmed else '✗ Pending'}</td>
        <td class="{'confirmed' if merchant_confirmed else 'pending'}">
          {'✓ Yes' if merchant_confirmed else '✗ Pending'}</td>
    </tr>
  </table>

  <h2>2. Goods &amp; Terms</h2>
  <table>
    <tr><td><b>Product</b></td><td>{product_name}</td></tr>
    <tr><td><b>Sector / Grade</b></td><td>{sector} — Grade {quality_grade}</td></tr>
    <tr><td><b>Quantity</b></td><td>{quantity:,.2f} {unit}</td></tr>
    <tr><td><b>Unit Price</b></td><td>ETB {price_per_unit:,.2f} / {unit}</td></tr>
    <tr class="total"><td><b>Total Value</b></td><td>ETB {total_price:,.2f}</td></tr>
    <tr><td><b>Delivery Date</b></td><td>{delivery_date or 'TBD'}</td></tr>
    <tr><td><b>Delivery Location</b></td><td>{delivery_location or 'TBD'}</td></tr>
    <tr><td><b>Payment Method</b></td><td>{payment_method}</td></tr>
    {'<tr><td><b>Notes</b></td><td>' + notes + '</td></tr>' if notes else ''}
  </table>

  <h2>3. Terms &amp; Conditions</h2>
  <ol>{terms_html}</ol>

  <h2>4. Signatures</h2>
  <div class="sig-box">
    <div class="sig">
      <div class="name">SELLER — {producer_name}</div>
      <div class="sig-line"></div>
      <div>Signature</div>
      <div style="margin-top:8px">Date: {today}</div>
    </div>
    <div class="sig">
      <div class="name">BUYER — {merchant_name}</div>
      <div class="sig-line"></div>
      <div>Signature</div>
      <div style="margin-top:8px">Date: {today}</div>
    </div>
  </div>

  <div class="footer">
    Ref: {ref} &nbsp;|&nbsp;
    Ethiopian AI Supply Chain Platform &nbsp;|&nbsp;
    This document is legally binding upon confirmation by both parties.
  </div>
</div>
</body>
</html>
"""


# ─────────────────────────────────────────────────────────────────────────────
# AGREEMENT WORKFLOW HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def build_agreement_payload(
    match: dict,
    producer: dict,
    product: dict,
    quantity: float,
    delivery_date: str,
    payment_method: str = "Bank Transfer",
    notes: str = "",
) -> dict:
    """
    Feature 2: Build a complete agreement payload when a producer
    selects the best match and sends an order.

    `match`   — merchant dict from the matching engine
    `producer`— logged-in producer dict
    `product` — product dict (name, sector, grade, unit, price_per_unit)

    Returns a dict ready to be stored in the DB and passed to
    generate_agreement_pdf() / generate_agreement_preview_html().
    """
    agreement_id = str(uuid.uuid4())
    price_per_unit = float(product.get("price_per_unit") or product.get("price", 0))
    total_price = price_per_unit * quantity

    return {
        "agreement_id":       agreement_id,
        "producer_id":        producer["id"],
        "merchant_id":        match["id"],
        "producer_name":      producer["name"],
        "producer_phone":     producer.get("phone", ""),
        "producer_region":    producer.get("region", ""),
        "merchant_name":      match["name"],
        "merchant_phone":     match.get("phone", ""),
        "merchant_region":    match.get("region", ""),
        "product_name":       product["name"],
        "sector":             product.get("sector", ""),
        "quality_grade":      product.get("grade", "A"),
        "quantity":           quantity,
        "unit":               product.get("unit", "kg"),
        "price_per_unit":     price_per_unit,
        "total_price":        total_price,
        "delivery_date":      delivery_date,
        "payment_method":     payment_method,
        "notes":              notes,
        "status":             "pending_merchant",   # workflow state
        "producer_confirmed": True,                 # producer initiates
        "merchant_confirmed": False,
        "created_at":         datetime.datetime.utcnow().isoformat(),
        "auto_sent_to_merchant": True,              # Feature 5 flag
    }


def producer_request_agreement(match: dict, producer: dict, product: dict,
                                quantity: float, delivery_date: str,
                                payment_method: str = "Bank Transfer",
                                notes: str = "") -> tuple[dict, bytes, str]:
    """
    Feature 2 + 5: One-call helper that:
      1. Builds the agreement payload
      2. Generates the PDF bytes
      3. Generates the HTML preview
      4. Returns (payload, pdf_bytes, html_preview) — backend stores payload,
         sends pdf_bytes to merchant via notification/email.
    """
    payload = build_agreement_payload(
        match, producer, product, quantity, delivery_date, payment_method, notes
    )
    pdf_bytes = generate_agreement_pdf(**{
        k: v for k, v in payload.items()
        if k in generate_agreement_pdf.__code__.co_varnames
    })
    html_preview = generate_agreement_preview_html(**{
        k: v for k, v in payload.items()
        if k in generate_agreement_preview_html.__code__.co_varnames
    })
    return payload, pdf_bytes, html_preview


def merchant_confirm_agreement(payload: dict) -> tuple[dict, bytes]:
    """
    Feature 3: Merchant confirms agreement.
    Updates payload, regenerates PDF with confirmed status, returns both.
    """
    payload = {**payload, "merchant_confirmed": True, "status": "confirmed"}
    pdf_bytes = generate_agreement_pdf(**{
        k: v for k, v in payload.items()
        if k in generate_agreement_pdf.__code__.co_varnames
    })
    return payload, pdf_bytes


def get_agreement_pdf_for_user(payload: dict, user_role: str = "any") -> bytes:
    """
    Feature 4: Any user (producer, merchant, admin) can call this to
    obtain the agreement PDF bytes for download.

    `user_role` is informational — all roles are permitted.
    """
    return generate_agreement_pdf(**{
        k: v for k, v in payload.items()
        if k in generate_agreement_pdf.__code__.co_varnames
    })
