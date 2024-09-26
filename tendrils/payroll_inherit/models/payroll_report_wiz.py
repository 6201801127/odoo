import base64
import os
from datetime import datetime
from datetime import *
from io import BytesIO

import xlsxwriter
from PIL import Image as Image
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from xlsxwriter.utility import xl_rowcol_to_cell


class payrollreportexcelwiz(models.TransientModel):
    _name = 'payroll.report.wiz'
    _description = 'payroll.report.wiz'

    from_date = fields.Date('From Date', required=True, default=lambda self: self.env.context.get('date_start'))
    date_end = fields.Date('To Date', required=True, default=lambda self: self.env.context.get('date_end'))
    company = fields.Many2one('res.company', default=lambda self: self.env['res.company']._company_default_get(),
                              string="Company")
    name = fields.Char('Name', default=lambda self: self.env.context.get('name'))

    # to get salary rules names
    @api.multi
    def get_rules(self):
        vals = []

        # heads = self.env['hr.salary.rule'].search([('active', '=', True),('code','not in',['GRATUITY','EPF','CHEAONE','CHEATWO','CHOTWO','CHOONE'])], order='sequence asc')
        heads = self.env['hr.salary.rule'].search([('active', '=', True), ('appears_on_payslip', '=', True),
                                                   ('code', 'not in', ['CHEAONE', 'CHEATWO', 'CHOTWO', 'CHOONE'])],
                                                  order='sequence asc')
        list = []
        for head in heads:
            list = [head.name, head.code]
            vals.append(list)

        return vals

    @api.multi
    def get_item_data(self, ):
        file_name = _('payroll report.xlsx')
        fp = BytesIO()

        workbook = xlsxwriter.Workbook(fp)
        heading_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True, 'size': 14})
        cell_text_format_n = workbook.add_format({'align': 'center', 'bold': True, 'size': 9, })
        cell_text_format = workbook.add_format({'align': 'left', 'bold': True, 'size': 9, })

        cell_text_format.set_border()
        cell_text_format_new = workbook.add_format({'align': 'left', 'size': 9, })
        cell_text_format_new.set_border()
        cell_number_format = workbook.add_format(
            {'align': 'right', 'bold': False, 'size': 9, 'num_format': '#,###0.00'})
        cell_number_format.set_border()
        worksheet = workbook.add_worksheet('payroll report.xlsx')
        normal_num_bold = workbook.add_format({'bold': True, 'num_format': '#,###0.00', 'size': 9, })
        normal_num_bold.set_border()
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('E:E', 20)
        worksheet.set_column('F:F', 20)
        worksheet.set_column('G:G', 20)
        worksheet.set_column('H:H', 20)
        worksheet.set_column('I:I', 20)
        worksheet.set_column('J:J', 20)
        worksheet.set_column('K:K', 20)
        worksheet.set_column('L:L', 20)
        worksheet.set_column('M:M', 20)
        worksheet.set_column('N:N', 20)

        if self.from_date and self.date_end:
            date_2 = datetime.strftime(self.date_end, '%d-%m-%Y')
            date_1 = datetime.strftime(self.from_date, '%d-%m-%Y')
            payroll_month = self.from_date.strftime("%B")
            worksheet.merge_range('A1:F2', '%s' % (self.name), heading_format)
            worksheet.merge_range('B4:D4', '%s' % (self.company.name), cell_text_format_n)
            row = 2
            column = 0
            worksheet.write(row + 1, 0, 'Company', cell_text_format_n)
            worksheet.write(row, 4, 'Date From', cell_text_format_n)
            worksheet.write(row, 5, date_1 or '')
            row += 1
            worksheet.write(row, 4, 'Date To', cell_text_format_n)
            worksheet.write(row, 5, date_2 or '')
            row += 2
            res = self.get_rules()

            worksheet.write(row, 0, 'Employee', cell_text_format)
            worksheet.write(row, 1, 'Department', cell_text_format)
            worksheet.write(row, 2, 'Employment Type', cell_text_format)

            row_set = row
            column = 3
            # to write salary rules names in the row
            for vals in res:
                worksheet.write(row, column, vals[0], cell_text_format)
                column += 1
            row += 1
            col = 0
            ro = row
            batch_id = int(self.env.context.get('payslip_id'))
            # payslip_ids=self.env['hr.payslip'].search([('date_from','=',self.from_date),('date_to','=',self.date_end),('state','=','done')])
            payslip_ids = self.env['hr.payslip.run'].search([('id', '=', batch_id)])

            if payslip_ids:
                for payslip in payslip_ids.slip_ids:
                    name = payslip.employee_id.name
                    department_id = payslip.employee_id.department_id.name
                    emp_type = payslip.employee_id.employement_type.name

                    worksheet.write(ro, col, name or '', cell_text_format_new)
                    worksheet.write(ro, col + 1, department_id or '', cell_text_format_new)
                    worksheet.write(ro, col + 2, emp_type or '', cell_text_format_new)

                    ro = ro + 1
            col = col + 3
            colm = col

            if payslip_ids:
                for slip in payslip_ids.slip_ids:
                    for payslip in slip:
                        for vals in res:

                            check = False
                            for line in payslip.line_ids:
                                if line.code == vals[1]:
                                    check = True
                                    r = line.total

                            if check == True:
                                worksheet.write(row, col, r, cell_number_format)
                            else:
                                worksheet.write(row, col, 0, cell_number_format)

                            col += 1
                        row += 1
                        col = colm
        worksheet.write(row, 0, 'Grand Total', cell_text_format)
        # calculating sum of column
        roww = row
        columnn = 3
        for vals in res:
            cell1 = xl_rowcol_to_cell(row_set + 1, columnn)
            cell2 = xl_rowcol_to_cell(row - 1, columnn)
            worksheet.write_formula(row, columnn, '{=SUM(%s:%s)}' % (cell1, cell2), normal_num_bold)
            columnn = columnn + 1

        worksheet.write(row, 1, '', cell_text_format)
        worksheet.write(row, 2, '', cell_text_format)

        workbook.close()
        file_download = base64.b64encode(fp.getvalue())
        fp.close()
        self = self.with_context(default_name=file_name, default_file_download=file_download)

        return {
            'name': 'payroll report Download',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'payroll.report.excel',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': self._context,
        }


class payroll_report_excel(models.TransientModel):
    _name = 'payroll.report.excel'
    _description = 'payroll.report.excel'

    name = fields.Char('File Name', size=256, readonly=True)
    file_download = fields.Binary('Download payroll', readonly=True)
