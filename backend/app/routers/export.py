from __future__ import annotations

from io import BytesIO

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from ..schemas.models import ExportFormat, ExportRequest

router = APIRouter(tags=["Export"])


def _safe_filename(stem: str) -> str:
	cleaned = "".join(ch for ch in stem.strip() if ch.isalnum() or ch in {" ", "-", "_"})
	return "_".join(cleaned.split()) or "study_aid"


def _build_pdf_bytes(title: str, content: str) -> bytes:
	from fpdf import FPDF

	pdf = FPDF()
	pdf.set_auto_page_break(auto=True, margin=15)
	pdf.add_page()

	effective_width = getattr(pdf, "epw", pdf.w - pdf.l_margin - pdf.r_margin)

	pdf.set_font("Helvetica", size=14)
	pdf.multi_cell(effective_width, 10, title)

	pdf.ln(2)
	pdf.set_font("Helvetica", size=11)
	pdf.multi_cell(effective_width, 6, content)

	out = pdf.output(dest="S")
	if isinstance(out, str):
		return out.encode("latin-1")
	return bytes(out)


def _build_docx_bytes(title: str, content: str) -> bytes:
	from docx import Document

	doc = Document()
	doc.add_heading(title, level=1)
	doc.add_paragraph(content)

	buf = BytesIO()
	doc.save(buf)
	return buf.getvalue()


@router.post(
	"/export",
	summary="Export a study aid as PDF or Word",
)
async def export(payload: ExportRequest) -> StreamingResponse:
	"""Exports a study aid as a downloadable PDF or DOCX."""

	title = payload.title or "Study Aid"
	safe_stem = _safe_filename(title)

	if payload.format == ExportFormat.pdf:
		data = _build_pdf_bytes(title=title, content=payload.content)
		filename = f"{safe_stem}.pdf"
		media_type = "application/pdf"
	else:
		data = _build_docx_bytes(title=title, content=payload.content)
		filename = f"{safe_stem}.docx"
		media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

	headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
	return StreamingResponse(BytesIO(data), media_type=media_type, headers=headers)
