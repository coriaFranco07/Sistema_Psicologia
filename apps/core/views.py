import html
import textwrap
import unicodedata

from django.http import HttpResponse
from django.utils.encoding import force_str

from apps.parametro.models.estado import Estado


def get_estado_activo():
    return Estado.objects.filter(dsc_estado__iexact="ACTIVO", flg_activo=True).first()


def get_estado_inactivo():
    return Estado.objects.filter(dsc_estado__iexact="INACTIVO", flg_activo=True).first()


def _normalize_export_value(value):
    if value is None:
        return ""
    return force_str(value).strip()


def _normalize_pdf_text(value):
    text = _normalize_export_value(value)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return text.replace("\r", " ").replace("\n", " ")


def _escape_pdf_text(value):
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def build_excel_table_response(filename, headers, rows):
    table_rows = [
        "<tr>" + "".join(f"<th>{html.escape(header)}</th>" for header in headers) + "</tr>"
    ]

    for row in rows:
        table_rows.append(
            "<tr>"
            + "".join(f"<td>{html.escape(_normalize_export_value(value))}</td>" for value in row)
            + "</tr>"
        )

    content = (
        "<html><head><meta charset='utf-8'></head><body>"
        "<table border='1'>"
        f"{''.join(table_rows)}"
        "</table></body></html>"
    )

    response = HttpResponse(
        content,
        content_type="application/vnd.ms-excel; charset=utf-8",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}.xls"'
    return response


def build_simple_pdf_response(filename, title, headers, rows):
    lines = [_normalize_pdf_text(title), ""]
    lines.extend(textwrap.wrap(" | ".join(headers), width=96) or [""])
    lines.append("-" * 96)

    for row in rows:
        row_text = " | ".join(_normalize_pdf_text(value) for value in row)
        lines.extend(textwrap.wrap(row_text, width=96) or [""])

    max_lines_per_page = 46
    pages = [
        lines[index:index + max_lines_per_page]
        for index in range(0, len(lines), max_lines_per_page)
    ] or [[]]

    page_objects = []
    content_objects = []
    page_contents = []

    for page_lines in pages:
        stream_lines = ["BT", "/F1 10 Tf", "14 TL", "48 794 Td"]
        for line in page_lines:
            stream_lines.append(f"({_escape_pdf_text(line)}) Tj")
            stream_lines.append("T*")
        stream_lines.append("ET")
        stream = "\n".join(stream_lines)
        page_contents.append(stream)

    total_pages = len(pages)
    font_object_number = 3 + total_pages * 2

    objects = [
        "<< /Type /Catalog /Pages 2 0 R >>",
        None,
    ]

    kids = []
    for index, stream in enumerate(page_contents):
        page_object_number = 3 + index * 2
        content_object_number = 4 + index * 2
        kids.append(f"{page_object_number} 0 R")
        page_objects.append(
            "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
            f"/Resources << /Font << /F1 {font_object_number} 0 R >> >> "
            f"/Contents {content_object_number} 0 R >>"
        )
        content_objects.append(
            f"<< /Length {len(stream.encode('latin-1', errors='ignore'))} >>\nstream\n"
            f"{stream}\nendstream"
        )

    objects[1] = f"<< /Type /Pages /Count {total_pages} /Kids [{' '.join(kids)}] >>"

    for page_object, content_object in zip(page_objects, content_objects):
        objects.append(page_object)
        objects.append(content_object)

    objects.append("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    pdf_parts = ["%PDF-1.4\n"]
    offsets = [0]

    for index, obj in enumerate(objects, start=1):
        offsets.append(sum(len(part.encode("latin-1")) for part in pdf_parts))
        pdf_parts.append(f"{index} 0 obj\n{obj}\nendobj\n")

    xref_offset = sum(len(part.encode("latin-1")) for part in pdf_parts)
    pdf_parts.append(f"xref\n0 {len(objects) + 1}\n")
    pdf_parts.append("0000000000 65535 f \n")

    for offset in offsets[1:]:
        pdf_parts.append(f"{offset:010d} 00000 n \n")

    pdf_parts.append(
        "trailer\n"
        f"<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF"
    )

    response = HttpResponse(
        "".join(pdf_parts).encode("latin-1", errors="ignore"),
        content_type="application/pdf",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}.pdf"'
    return response


class TableListSupportMixin:
    default_page_size = 10
    allowed_page_sizes = (5, 10)
    export_filename = "registros"
    export_title = "Listado"

    def get_selected_page_size(self):
        raw_value = force_str(self.request.GET.get("per_page", "")).strip().lower()
        if raw_value == "all":
            return "all"
        if raw_value.isdigit():
            value = int(raw_value)
            if value in self.allowed_page_sizes:
                return value
        return self.default_page_size

    def get_paginate_by(self, queryset):
        selected_page_size = self.get_selected_page_size()
        if selected_page_size == "all":
            return None
        return selected_page_size

    def get_page_size_options(self):
        return [
            {"value": str(size), "label": str(size)}
            for size in self.allowed_page_sizes
        ] + [{"value": "all", "label": "Todos"}]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        object_list = context.get("object_list", [])
        if context.get("is_paginated"):
            total_count = context["paginator"].count
        else:
            total_count = len(object_list)
        context["selected_per_page"] = str(self.get_selected_page_size())
        context["per_page_options"] = self.get_page_size_options()
        context["table_total_count"] = total_count
        context["table_export_enabled"] = bool(self.get_export_columns())
        return context

    def render_to_response(self, context, **response_kwargs):
        export_format = force_str(self.request.GET.get("export", "")).strip().lower()
        if export_format in {"excel", "pdf"}:
            queryset = self.get_export_queryset()
            headers, rows = self.build_export_rows(queryset)
            filename = self.get_export_filename()
            title = self.get_export_title()
            if export_format == "excel":
                return build_excel_table_response(filename, headers, rows)
            return build_simple_pdf_response(filename, title, headers, rows)
        return super().render_to_response(context, **response_kwargs)

    def get_export_queryset(self):
        return self.get_queryset()

    def get_export_columns(self):
        return []

    def get_export_filename(self):
        return self.export_filename

    def get_export_title(self):
        return self.export_title

    def build_export_rows(self, queryset):
        columns = self.get_export_columns()
        headers = [header for header, _ in columns]
        rows = []
        for obj in queryset:
            row = []
            for _, getter in columns:
                value = getter(obj) if callable(getter) else getattr(obj, getter, "")
                row.append(_normalize_export_value(value))
            rows.append(row)
        return headers, rows
