import pandas as pd
from io import BytesIO
from fastapi.responses import Response
from jinja2 import Template
from xhtml2pdf import pisa
from pathlib import Path
from crud.items_ordered import get_items_ordered

def generate_excel_report(session, order_id=None, user_id=None, item_id=None, skip=0, limit=100):
    items = get_items_ordered(session, order_id=order_id, user_id=user_id, item_id=item_id, skip=skip, limit=limit)
    buffer = BytesIO()
    data = [{
        "Order ID": item.order_id,
        "Item ID": item.item_id,
        "Item Title": item.title,
        "Item Description": item.description,
        "Item Category": item.category,
        "Item Price": item.price,
        "Item Rating": item.rating,
        "Item Brand": item.brand,
        "Item Quantity": item.quantity
    } for item in items]
    df = pd.DataFrame(data)
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Items Ordered")
    buffer.seek(0)
    return Response(
        buffer.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=items_ordered.xlsx"}
    )

def generate_csv_report(session, order_id=None, user_id=None, item_id=None, skip=0, limit=100):
    items = get_items_ordered(session, order_id=order_id, user_id=user_id, item_id=item_id, skip=skip, limit=limit)
    buffer = BytesIO()
    data = [{
        "Order ID": item.order_id,
        "Item ID": item.item_id,
        "Item Title": item.title,
        "Item Description": item.description,
        "Item Category": item.category,
        "Item Price": item.price,
        "Item Rating": item.rating,
        "Item Brand": item.brand,
        "Item Quantity": item.quantity
    } for item in items]
    df = pd.DataFrame(data)
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    return Response(
        buffer.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=items_ordered.csv"}
    )

def generate_pdf_report(session, order_id=None, user_id=None, item_id=None, skip=0, limit=100):
    items = get_items_ordered(session, order_id=order_id, user_id=user_id, item_id=item_id, skip=skip, limit=limit)
    template_path = Path("templates/order_template.html")
    html_template = template_path.read_text(encoding="utf-8")
    template = Template(html_template)
    rendered_html = template.render(items=[{
        "order_id": item.order_id,
        "item_id": item.item_id,
        "title": item.title,
        "description": item.description,
        "category": item.category,
        "price": item.price,
        "rating": item.rating,
        "brand": item.brand,
        "quantity": item.quantity
    } for item in items])

    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(rendered_html, dest=pdf_buffer)
    if pisa_status.err:
        return {"error": "Error al generar el PDF"}
    pdf_buffer.seek(0)
    
    return Response(
        pdf_buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=items_ordered.pdf"}
    )