import io
from datetime import datetime
from fpdf import FPDF
import cloudinary.uploader
from app.utils.cloudinary_helper import cloudinary  # reuse configured cloudinary instance

# ── Colour palette ──────────────────────────────────────────────────────────
GREY   = (89, 89, 89)      # header background / accent lines
IVORY  = (253, 252, 248)   # page background
WHITE  = (255, 255, 255)
BLACK  = (30,  30,  30)    # body text
LIGHT  = (220, 220, 215)   # table row alternate / border


class InvoicePDF(FPDF):
    def __init__(self, order_id: int):
        super().__init__()
        self.order_id = order_id
        self.set_auto_page_break(auto=True, margin=15)

    # ── Header ───────────────────────────────────────────────────────────────
    def header(self):
        # Grey top bar
        self.set_fill_color(*GREY)
        self.rect(0, 0, 210, 28, "F")

        # Company name (left)
        self.set_xy(12, 8)
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(*WHITE)
        self.cell(100, 10, "My Store", ln=0)

        # "INVOICE" label (right)
        self.set_font("Helvetica", "B", 20)
        self.set_xy(140, 6)
        self.cell(58, 14, "INVOICE", ln=0, align="R")

        # Ivory page background (below header)
        self.set_fill_color(*IVORY)
        self.rect(0, 28, 210, 269, "F")

    # ── Footer ───────────────────────────────────────────────────────────────
    def footer(self):
        self.set_y(-14)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*GREY)
        self.cell(0, 6, "Thank you for shopping with us!", align="C")


def _draw_section_label(pdf: FPDF, label: str):
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*GREY)
    pdf.cell(0, 5, label.upper(), ln=True)
    pdf.set_draw_color(*LIGHT)
    pdf.set_line_width(0.3)
    pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 186, pdf.get_y())
    pdf.ln(2)


def _meta_row(pdf: FPDF, label: str, value: str):
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*GREY)
    pdf.cell(45, 6, label, ln=0)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*BLACK)
    pdf.cell(0, 6, value, ln=True)


def generate_invoice_pdf(
    order_id: int,
    user_name: str,
    user_email: str,
    shipping_address: str | None,
    razorpay_payment_id: str | None,
    total_amount: int,
    items: list[dict],
    created_at: datetime,
) -> bytes:
    pdf = InvoicePDF(order_id=order_id)
    pdf.add_page()
    pdf.set_text_color(*BLACK)

    # ── Meta block ───────────────────────────────────────────────────────────
    pdf.set_xy(12, 36)
    _draw_section_label(pdf, "Invoice Details")

    pdf.set_x(12)
    _meta_row(pdf, "Invoice No :", f"INV-{order_id:05d}")
    pdf.set_x(12)
    _meta_row(pdf, "Date :", created_at.strftime("%d %b %Y"))
    pdf.set_x(12)
    _meta_row(pdf, "Payment ID :", razorpay_payment_id or "—")
    pdf.ln(4)

    # ── Customer block ───────────────────────────────────────────────────────
    pdf.set_x(12)
    _draw_section_label(pdf, "Billed To")
    pdf.set_x(12)
    _meta_row(pdf, "Name :", user_name)
    pdf.set_x(12)
    _meta_row(pdf, "Email :", user_email)
    if shipping_address:
        pdf.set_x(12)
        _meta_row(pdf, "Address :", shipping_address)
    pdf.ln(6)

    # ── Items table header ───────────────────────────────────────────────────
    pdf.set_x(12)
    _draw_section_label(pdf, "Order Items")
    pdf.ln(1)

    col_w = [10, 75, 30, 25, 25, 27]   # #, Product, SKU, Qty, Unit Price, Subtotal
    headers = ["#", "Product", "SKU", "Qty", "Unit Price", "Subtotal"]

    pdf.set_fill_color(*GREY)
    pdf.set_text_color(*WHITE)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_x(12)
    for i, h in enumerate(headers):
        align = "C" if i in (0, 3) else "L"
        pdf.cell(col_w[i], 8, h, border=0, ln=0, align=align, fill=True)
    pdf.ln(8)

    # ── Items rows ───────────────────────────────────────────────────────────
    pdf.set_font("Helvetica", "", 9)
    for idx, item in enumerate(items):
        fill = idx % 2 == 0
        pdf.set_fill_color(*LIGHT) if fill else pdf.set_fill_color(*IVORY)
        pdf.set_text_color(*BLACK)
        pdf.set_x(12)

        unit_price = item["unit_price"]
        subtotal   = item["subtotal"]

        pdf.cell(col_w[0], 7, str(idx + 1),              fill=fill, align="C")
        pdf.cell(col_w[1], 7, item["product_name"][:35], fill=fill)
        pdf.cell(col_w[2], 7, item["product_sku"][:14],  fill=fill)
        pdf.cell(col_w[3], 7, str(item["quantity"]),     fill=fill, align="C")
        pdf.cell(col_w[4], 7, f"Rs {unit_price:,}",      fill=fill)
        pdf.cell(col_w[5], 7, f"Rs {subtotal:,}",        fill=fill)
        pdf.ln(7)

    pdf.ln(4)

    # ── Total ─────────────────────────────────────────────────────────────────
    pdf.set_x(12)
    pdf.set_draw_color(*GREY)
    pdf.set_line_width(0.5)
    pdf.line(12, pdf.get_y(), 198, pdf.get_y())
    pdf.ln(3)

    pdf.set_x(130)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_fill_color(*GREY)
    pdf.set_text_color(*WHITE)
    pdf.cell(40, 9, "TOTAL", fill=True, align="C")
    pdf.cell(28, 9, f"Rs {total_amount:,}", fill=True, align="C")
    pdf.ln(14)

    # ── Thank-you note ───────────────────────────────────────────────────────
    pdf.set_x(12)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(*GREY)
    pdf.cell(0, 6, "This is a system-generated invoice. No signature required.", align="C")

    return bytes(pdf.output())


def upload_invoice(pdf_bytes: bytes, order_id: int) -> str:
    result = cloudinary.uploader.upload(
        pdf_bytes,
        folder="invoices",
        public_id=f"invoice_order_{order_id}",
        resource_type="raw",
        format="pdf",
    )
    return result["secure_url"]
