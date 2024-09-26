from datetime import date, datetime, timezone, timedelta
from odoo import models, fields, api, exceptions
from odoo.exceptions import ValidationError
from io import BytesIO
import xlsxwriter
import unicodedata
import base64
import re
from xlsxwriter.utility import xl_rowcol_to_cell
import calendar
from dateutil.relativedelta import relativedelta

class DownloadEpfReport(models.TransientModel):
    _name = "download_epf_report"
    _description = "Download EPF Report"

    @api.model
    def default_get(self, fields):
        res = super(DownloadEpfReport, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])

        res.update({
            'epf_details_ids': active_ids,
        })

        return res

    epf_details_ids = fields.Many2many(
        string='EPF Details',
        comodel_name='payroll_epf_calculation_report',
        relation='payroll_epf_calculation_report_rel',
        column1='epf_id',
        column2='report_id',
    )
    download_file = fields.Binary(string="Download Xls")

    @api.multi
    def download_epf_report(self):
        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)

        # heading_format = workbook.add_format({'align': 'left', 'valign': 'vcenter', 'bold': True, 'size': 14})
        # heading_format.set_border()

        cell_text_format_n = workbook.add_format({'align': 'left', 'bold': False, 'size': 9, })
        cell_text_format_n.set_border()

        cell_text_center_normal = workbook.add_format({'align': 'center', 'bold': True, 'size': 11, })
        cell_text_center_normal.set_border()

        cell_text_format = workbook.add_format({'align': 'left', 'bold': True, 'size': 11, })
        cell_text_format.set_border()

        # cell_text_format_new = workbook.add_format({'align': 'left', 'size': 9, })
        # cell_text_format_new.set_border()

        cell_text_amount_format =  workbook.add_format(
            {'align': 'right', 'bold': False, 'size': 9, 'num_format': '#,###0.00'})
        cell_text_amount_format.set_border()
        
        cell_number_format = workbook.add_format(
            {'align': 'right', 'bold': True, 'size': 9, 'num_format': '#,###0.00'})
        cell_number_format.set_border()

        # cell_date_format = workbook.add_format({'num_format': 'dd-mmm-yyyy', 'size': 9, })
        # cell_date_format.set_border()

        worksheet = workbook.add_worksheet(f'EPF')

        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('E:E', 20)
        worksheet.set_column('F:F', 20)
        worksheet.set_column('G:G', 20)
        worksheet.set_column('H:H', 20)
        worksheet.set_column('I:I', 20)
       
        row = 0
        worksheet.write(row, 0, 'Year', cell_text_center_normal)
        worksheet.write(row, 1, 'Month', cell_text_center_normal)
        worksheet.write(row, 2, 'UAN', cell_text_center_normal)
        worksheet.write(row, 3, 'Member Name', cell_text_center_normal)
        worksheet.write(row, 4, 'Gross Wages', cell_text_center_normal)
        worksheet.write(row, 5, 'EPF Wages', cell_text_center_normal)
        worksheet.write(row, 6, 'EPS Wages', cell_text_center_normal)
        worksheet.write(row, 7, 'EDLI Wages', cell_text_center_normal)
        worksheet.write(row, 8, 'Emp PF contribution ', cell_text_center_normal)
        worksheet.write(row, 9, 'EPS', cell_text_center_normal)
        worksheet.write(row, 10, 'Empr PF contribution ', cell_text_center_normal)

        row += 1
        col = 0
       
        for emp in self.epf_details_ids:
            month = calendar.month_name[int(emp.month)]
            worksheet.write(row, col, emp.year or '', cell_text_format_n)
            worksheet.write(row, col + 1, month or '', cell_text_format_n)
            worksheet.write(row, col + 2, emp.uan or '', cell_text_format_n)
            worksheet.write(row, col + 3, emp.employee_id.name or '', cell_text_format_n)
            worksheet.write(row, col + 4, emp.gross_wages or '', cell_text_amount_format)
            worksheet.write(row, col + 5, emp.gross_wages or '', cell_text_amount_format)
            worksheet.write(row, col + 6, emp.eps_wages or '', cell_text_amount_format)
            worksheet.write(row, col + 7, emp.eps_wages or '', cell_text_amount_format)
            worksheet.write(row, col + 8, emp.employee_pf or '', cell_text_amount_format)
            worksheet.write(row, col + 9, emp.pension_fund or '', cell_text_amount_format)
            worksheet.write(row, col + 10, emp.employer_pf or '', cell_text_amount_format)
            row += 1
        gross_wages,eps_wages,employee_pf,pension_fund,employer_pf = 0,0,0,0,0
        for line in self.epf_details_ids:
            gross_wages += line.gross_wages
            worksheet.write(row, col+4, gross_wages, cell_number_format)
            worksheet.write(row, col+5, gross_wages, cell_number_format)
            eps_wages += line.eps_wages
            worksheet.write(row, col+6, eps_wages, cell_number_format)
            worksheet.write(row, col+7, eps_wages, cell_number_format)
            employee_pf += line.employee_pf
            worksheet.write(row, col+8, employee_pf, cell_number_format)
            pension_fund += line.pension_fund
            worksheet.write(row, col+9, pension_fund, cell_number_format)
            employer_pf += line.employer_pf
            worksheet.write(row, col+10, employer_pf, cell_number_format)

        row += 1

        worksheet.write(row-1, 3, 'Total', cell_text_center_normal)
        workbook.close()
        fp.seek(0)
        self.download_file = base64.b64encode(fp.read())
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/download_epf_report/%s/download_file/EPF Calculation Report.xls?download=true' % (
                self.id)
        }
        
    def slugify(self, value):
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
        value = re.sub('[^\w\s-]', '', value).strip().lower()
        return re.sub('[-\s]+', '-', value)

    
  