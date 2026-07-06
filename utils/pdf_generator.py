"""PDF generation for agreements."""
import io
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER
from utils.constants import AGREEMENT_TERMS


def generate_agreement_pdf(
    producer_name, producer_phone, producer_region,
    merchant_name, merchant_phone, merchant_region,
    product_name, sector, quality_grade,
    quantity, unit, price_per_unit, total_price,
    delivery_date, payment_method, notes,
    agreement_id, producer_confirmed=False, merchant_confirmed=False,
):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("T", parent=styles["Title"], fontSize=18, textColor=colors.HexColor("#1B4332"), alignment=TA_CENTER, spaceAfter=6)
    section_style = ParagraphStyle("H", parent=styles["Heading2"], fontSize=12, textColor=colors.HexColor("#1B4332"), spaceBefore=14, spaceAfter=6)
    body_style = ParagraphStyle("B", parent=styles["Normal"], fontSize=10, leading=16, spaceAfter=4)
    footer_style = ParagraphStyle("F", parent=styles["Normal"], fontSize=7, textColor=colors.HexColor("#999999"), alignment=TA_CENTER)

    story = []
    story.append(Paragraph("Ethiopian AI Supply Chain Platform", styles["Title"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph("COMMERCIAL SUPPLY AGREEMENT", title_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"Reference: AGR-{agreement_id[:8].upper()}", body_style))
    story.append(Paragraph(f"Date: {datetime.date.today().strftime('%d %B %Y')}", body_style))
    story.append(Spacer(1, 14))
    story.append(Paragraph("1. PARTIES", section_style))
    story.append(Paragraph(f"<b>Seller:</b> {producer_name} ({producer_region})", body_style))
    story.append(Paragraph(f"<b>Buyer:</b> {merchant_name} ({merchant_region})", body_style))
    story.append(Spacer(1, 14))
    story.append(Paragraph("2. GOODS & TERMS", section_style))
    story.append(Paragraph(f"<b>Product:</b> {product_name} ({sector}, Grade {quality_grade})", body_style))
    story.append(Paragraph(f"<b>Quantity:</b> {quantity:,.1f} {unit}", body_style))
    story.append(Paragraph(f"<b>Price:</b> {price_per_unit:,.2f} Birr/unit", body_style))
    story.append(Paragraph(f"<b>Total:</b> {total_price:,.2f} Birr", body_style))
    story.append(Paragraph(f"<b>Delivery:</b> {delivery_date}", body_style))
    story.append(Paragraph(f"<b>Payment:</b> {payment_method}", body_style))
    story.append(Spacer(1, 14))
    story.append(Paragraph("3. TERMS AND CONDITIONS", section_style))
    for heading, text in AGREEMENT_TERMS:
        story.append(Paragraph(f"<b>{heading}:</b> {text}", body_style))
        story.append(Spacer(1, 4))
    story.append(Spacer(1, 20))
    story.append(Paragraph("Signatures:", section_style))
    story.append(Spacer(1, 30))
    story.append(Paragraph(f"Producer: {producer_name}  ___________________", body_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"Merchant: {merchant_name}  ___________________", body_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"Generated: {datetime.datetime.now().strftime('%d %B %Y, %H:%M')} | Ref: AGR-{agreement_id[:8].upper()}", footer_style))
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
