import io
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.views import View
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from openpyxl import Workbook

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

# Permission Required
class PermissionMixin(LoginRequiredMixin, PermissionRequiredMixin):
    """
    Custom mixin that ensures the user has the required permission(s) OR is a superuser.
    """
    def has_permission(self):
        user = self.request.user
        perms = self.get_permission_required()
        if isinstance(perms, str):
            perms = [perms]
        return user.is_authenticated and (user.has_perms(perms) or user.is_superuser)
    
# Export Mixin
class ExportMixin(View):
    model = None
    filename_prefix = "" 

    def get_object(self):
        return get_object_or_404(self.model, pk=self.kwargs.get("pk"))

    # --- PDF Export ---
    def render_to_pdf(self, obj, fields, extra_sections=None):
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        y = height - 50

        # Title
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, y, f"{self.model.__name__} Details - {obj}")
        y -= 30

        # Main fields
        p.setFont("Helvetica", 12)
        for label, value in fields:
            p.drawString(50, y, f"{label}: {value}")
            y -= 20

        # Extra sections (like accessories, devices, history…)
        if extra_sections:
            for section_title, lines in extra_sections:
                y -= 20
                p.setFont("Helvetica-Bold", 13)
                p.drawString(50, y, f"{section_title}:")
                y -= 20
                p.setFont("Helvetica", 12)
                if lines:
                    for line in lines:
                        p.drawString(70, y, f"- {line}")
                        y -= 15
                else:
                    p.drawString(70, y, "- None")

        p.showPage()
        p.save()
        buffer.seek(0)
        return buffer

    def export_pdf(self, request, *args, **kwargs):
        obj = self.get_object()
        buffer = self.render_to_pdf(*self.get_pdf_content(obj))
        return FileResponse(
            buffer,
            as_attachment=True,
            filename=f"{self.filename_prefix}_{obj.pk}.pdf"
        )

    # --- Excel Export ---
    def render_to_excel(self, obj, sheets):
        wb = Workbook()
        for idx, (title, rows) in enumerate(sheets):
            ws = wb.active if idx == 0 else wb.create_sheet(title)
            ws.title = title
            for row in rows:
                ws.append(row)
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = f'attachment; filename={self.filename_prefix}_{obj.pk}.xlsx'
        wb.save(response)
        return response

    def export_excel(self, request, *args, **kwargs):
        obj = self.get_object()
        return self.render_to_excel(obj, self.get_excel_content(obj))

    # --- Methods to implement in subclass ---
    def get_pdf_content(self, obj):
        """return (obj, fields, extra_sections)"""
        raise NotImplementedError

    def get_excel_content(self, obj):
        """return [(sheet_title, rows)]"""
        raise NotImplementedError

