from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import io

from database.dependencies import get_session
from api.services import report_service

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get(
    "/sales",
    summary="Скачать отчет по продажам в формате DOCX",
)
async def download_sales_report(
        session: AsyncSession = Depends(get_session),
):
    """
    Генерирует и возвращает DOCX-файл с отчетом по продажам мерча.
    Отчет содержит статистику и топ-5 самых продаваемых товаров.
    """
    docx_bytes = await report_service.generate_sales_report_docx(session)

    return StreamingResponse(
        io.BytesIO(docx_bytes),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": "attachment; filename=spar_merch_sales_report.docx"
        },
    )