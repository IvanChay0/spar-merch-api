import io
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

from database.tables.entities.merch_item import MerchItem
from database.tables.junctions.purchase import Purchase
from database.tables.entities.employee import Employee


async def generate_sales_report_docx(session: AsyncSession) -> bytes:
    """Генерирует DOCX отчет о продажах и возвращает его как байты."""

    # 1. Собираем статистику из БД
    total_employees_res = await session.execute(select(func.count(Employee.id)))
    total_employees = total_employees_res.scalar() or 0

    total_items_res = await session.execute(select(func.count(MerchItem.id)))
    total_items = total_items_res.scalar() or 0

    total_purchases_res = await session.execute(select(func.count(Purchase.id)))
    total_purchases = total_purchases_res.scalar() or 0

    total_revenue_res = await session.execute(
        select(func.sum(MerchItem.price)).select_from(Purchase).join(MerchItem, Purchase.merch_item_id == MerchItem.id)
    )
    total_revenue = total_revenue_res.scalar() or 0.0

    # Топ-5 самых продаваемых товаров
    top_items_res = await session.execute(
        select(MerchItem.name, func.count(Purchase.id).label('count'), func.sum(MerchItem.price).label('revenue'))
        .join(Purchase, MerchItem.id == Purchase.merch_item_id)
        .group_by(MerchItem.id, MerchItem.name)
        .order_by(func.count(Purchase.id).desc())
        .limit(5)
    )
    top_items = top_items_res.all()

    # 2. Создаем документ Word
    doc = Document()

    # Заголовок
    title = doc.add_heading('Отчет по продажам мерча SPAR', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Дата формирования
    date_p = doc.add_paragraph(f'Дата формирования: {datetime.now().strftime("%d.%m.%Y %H:%M")}')
    date_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    doc.add_paragraph('_' * 50)

    # Сводная статистика
    doc.add_heading('1. Сводная статистика', level=1)
    stats_table = doc.add_table(rows=4, cols=2)
    stats_table.style = 'Light Shading Accent 1'

    stats_data = [
        ("Всего сотрудников в системе", str(total_employees)),
        ("Всего товаров в каталоге", str(total_items)),
        ("Совершено покупок", str(total_purchases)),
        ("Общая выручка (монеты)", f"{total_revenue:.2f}")
    ]

    for i, (label, value) in enumerate(stats_data):
        stats_table.cell(i, 0).text = label
        stats_table.cell(i, 1).text = value

    doc.add_paragraph('\n')

    # Топ товаров
    doc.add_heading('2. Топ-5 самых популярных товаров', level=1)

    if top_items:
        top_table = doc.add_table(rows=1, cols=3)
        top_table.style = 'Medium Grid 1 Accent 1'
        hdr_cells = top_table.rows[0].cells
        hdr_cells[0].text = 'Название товара'
        hdr_cells[1].text = 'Кол-во продаж'
        hdr_cells[2].text = 'Выручка (монеты)'

        # Делаем заголовок жирным
        for cell in hdr_cells:
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.bold = True

        for item_name, count, revenue in top_items:
            row_cells = top_table.add_row().cells
            row_cells[0].text = item_name
            row_cells[1].text = str(count)
            row_cells[2].text = f"{revenue:.2f}"
    else:
        doc.add_paragraph('Покупок пока не было.')

    # 3. Сохраняем в память (BytesIO), чтобы не писать на диск
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    return buffer.read()