# from odoo import models
# from docx import Document
# import xlsxwriter



# class PartnerDocx(models.AbstractModel):
#     _name = 'report.report_docx.partner_docx'
#     _inherit = 'report.report_docx.abstract'

#     def generate_docx_report(self, document, data, partners):
#         workbook = xlsxwriter.Workbook(document)        
#         for obj in partners:
#             sheet = document.add_worksheet('Report')
#             bold = workbook.add_format({'bold': True})
#             sheet.write(0, 0, obj.name, bold)
