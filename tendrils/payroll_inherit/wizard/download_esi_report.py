from datetime import date, datetime, timezone, timedelta
from odoo import models, fields, api, exceptions
from odoo.exceptions import ValidationError
from io import BytesIO
import xlsxwriter
import unicodedata
import base64
import re
from xlsxwriter.utility import xl_rowcol_to_cell
# from xlsxwriter import write_rich_string
import calendar
from dateutil.relativedelta import relativedelta
import calendar

class DownloadEsiReport(models.TransientModel):
    _name = "download_esi_report"
    _description = "Download ESI Report"

    @api.model
    def default_get(self, fields):
        res = super(DownloadEsiReport, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])

        res.update({
            'esi_details_ids': active_ids,
        })

        return res

    esi_details_ids = fields.Many2many(
        string='ESI Details',
        comodel_name='employee_esi_calc_report',
        relation='employee_esi_calc_report_rel',
        column1='esi_id',
        column2='report_id',
    )
    download_file = fields.Binary(string="Download Xls")

   
    @api.multi
    def download_esi_report(self):
        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)

        # heading_format = workbook.add_format({'align': 'left', 'valign': 'vcenter', 'bold': True, 'size': 14,'text_wrap': True})
        # heading_format.set_border()

        # cell_text_format_n = workbook.add_format({'align': 'center', 'bold': True, 'size': 9,'text_wrap': True })
        # cell_text_format_n.set_border()

        cell_text_center_normal = workbook.add_format({'align': 'top', 'bold': True, 'size': 11,'text_wrap': True })
        cell_text_center_normal.set_border()
        cell_text_center_normal.set_center_across()
        
        # cell_text_color = workbook.add_format({'align': 'center', 'bold': True, 'size': 11, 'font_color':'red','text_wrap': True })
        # cell_text_color.set_border()


        cell_text_format = workbook.add_format({'align': 'left', 'bold': False, 'size': 9, 'text_wrap': True})
        cell_text_format.set_border()

        # cell_text_format_new = workbook.add_format({'align': 'left', 'size': 9, 'text_wrap': True})
        # cell_text_format_new.set_border()

        cell_text_amount_format =  workbook.add_format(
            {'align': 'right', 'bold': False, 'size': 9, 'num_format': '#,###0.00','text_wrap': True})
        cell_text_amount_format.set_border()
        
        # cell_number_format = workbook.add_format(
        #     {'align': 'right', 'bold': True, 'size': 9, 'num_format': '#,###0.00','text_wrap': True})
        # cell_number_format.set_border()

        cell_date_format = workbook.add_format({'num_format': 'dd-mmm-yyyy', 'size': 9, 'text_wrap': True})
        cell_date_format.set_border()

        worksheet = workbook.add_worksheet(f'ESI')
        worksheet.set_row(0, 85)
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('E:E', 20)
        worksheet.set_column('F:F', 20)
        worksheet.set_column('G:G', 20)
        worksheet.set_column('H:H', 20)

       
        row = 0
        worksheet.write(row, 0, 'Year', cell_text_center_normal)
        worksheet.write(row, 1, 'Month', cell_text_center_normal)
        worksheet.write(row, 2, 'IP Number (10 Digits)', cell_text_center_normal)
        worksheet.write(row, 3, 'IP Name( Only alphabets and space )', cell_text_center_normal)
        worksheet.write(row, 4, 'No of Days for which wages paid/payable during the month', cell_text_center_normal)
        worksheet.write(row, 5, 'Total Monthly Wages', cell_text_center_normal)
        worksheet.write(row, 6, 'Reason Code for Zero workings days(numeric only; provide 0 for all other reasons- Click on the link for reference)', cell_text_center_normal)
        worksheet.write(row, 7, 'Last Working Day( Format DD/MM/YYYY  or DD-MM-YYYY)', cell_text_center_normal)

        row += 1
        col = 0
        for emp in self.esi_details_ids:
            attendance = self.env['kw_payroll_monthly_attendance_report'].sudo().search([('employee_id','=',emp.employee_id.id),('attendance_year','=',int(emp.year)),('attendance_month','=',int(emp.month))],limit=1).actual_working
            month = calendar.month_name[int(emp.month)]
            worksheet.write(row, col, emp.year or '', cell_text_format)
            worksheet.write(row, col + 1, month or '', cell_text_format)
            worksheet.write(row, col + 2, emp.contract_id.esi_id or '', cell_text_format)
            worksheet.write(row, col + 3, emp.employee_id.name or '', cell_text_format)
            worksheet.write(row, col + 4, attendance or '', cell_text_amount_format)
            worksheet.write(row, col + 5, emp.basic or '', cell_text_amount_format)
            worksheet.write(row, col + 6, '' , cell_text_amount_format)
            worksheet.write(row, col + 7, emp.employee_id.last_working_day or '', cell_date_format)
            row += 1
            
        workbook.close()
        fp.seek(0)
        self.download_file = base64.b64encode(fp.read())
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/download_esi_report/%s/download_file/ESI Calculation Report.xls?download=true' % (
                self.id)
        }
        
    def slugify(self, value):
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
        value = re.sub('[^\w\s-]', '', value).strip().lower()
        return re.sub('[-\s]+', '-', value)

    
  
  