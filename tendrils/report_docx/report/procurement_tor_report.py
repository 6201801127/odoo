# -*- coding: utf-8 -*-

from odoo import models
import html2text


class ProcurementTORReport(models.AbstractModel):
    _name = 'report.report_docx.report_procurement_tor'
    _inherit = 'report.report_docx.abstract'

    def generate_docx_report(self, document, data, tors):
        if tors.section_ids:
            for section in tors.section_ids:
                document.add_heading(section.name.name, 0)
                document.add_paragraph(html2text.html2text(section.description))