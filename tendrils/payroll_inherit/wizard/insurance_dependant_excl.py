from odoo import models, fields, api, exceptions
from datetime import date, datetime, time
from io import BytesIO
import xlsxwriter
import unicodedata
import base64
import re


class InsuranceReport(models.TransientModel):
    _name = "employee_family_insurance_report"
    _description = "Employee relationship insurance report xl sheet"
    
    download_file = fields.Binary(string="Download Xls")
    finacial_year = fields.Many2one('account.fiscalyear', 'Financial Year')
    
    @api.multi
    def download_excl_insurance_report(self):
        file_name = self.slugify("Family Insurance Excel sheet") + ".xlsx"

        current_fiscal = self.env['account.fiscalyear'].search(
            [('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])

        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)

        heading_format = workbook.add_format({'align': 'left', 'valign': 'vcenter', 'bold': True, 'size': 14})
        heading_format.set_border()

        cell_text_format_n = workbook.add_format({'align': 'center', 'bold': True, 'size': 9, })
        cell_text_format_n.set_border()

        cell_text_center_normal = workbook.add_format({'align': 'center', 'bold': True, 'size': 11, })
        cell_text_center_normal.set_border()

        cell_text_format = workbook.add_format({'align': 'left', 'bold': True, 'size': 11, })
        cell_text_format.set_border()

        cell_text_format_new = workbook.add_format({'align': 'left', 'size': 9, })
        cell_text_format_new.set_border()

        cell_number_format = workbook.add_format(
            {'align': 'right', 'bold': False, 'size': 9, 'num_format': '#,###0.00'})
        cell_number_format.set_border()

        cell_date_format = workbook.add_format({'num_format': 'dd-mmm-yyyy', 'size': 9, })
        cell_date_format.set_border()

        worksheet = workbook.add_worksheet(f'Insurance Report')

        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('E:E', 20)
        worksheet.set_column('F:F', 20)
        worksheet.set_column('G:G', 20)
        row = 1
        worksheet.write(row, 0, 'Location', cell_text_center_normal)
        worksheet.write(row, 1, 'Department', cell_text_center_normal)
        worksheet.write(row, 2, 'Designation', cell_text_center_normal)
        worksheet.write(row, 3, 'Employee Code', cell_text_center_normal)
        worksheet.write(row, 4, 'Employee Name', cell_text_center_normal)
        worksheet.write(row, 5, 'Relation', cell_text_center_normal)
        worksheet.write(row, 6, 'Name', cell_text_center_normal)
        worksheet.write(row, 7, 'Gender', cell_text_center_normal)
        worksheet.write(row, 8, 'Date Of Birth', cell_text_center_normal)
        worksheet.write(row, 9, 'Approx. Premium', cell_text_center_normal)

        row += 1
        col = 0
        relationship_data = self.env['family_details'].sudo().search(
            [('family_details_id.date_range', '=', current_fiscal.id)])

        unique_emp = set(relationship_data.mapped('emp_name'))
        for emp in unique_emp:
            worksheet.write(row, col, emp.job_branch_id.alias or '', cell_text_format_new)
            worksheet.write(row, col + 1, emp.department_id.name or '', cell_text_format_new)
            worksheet.write(row, col + 2, emp.job_id.name or '', cell_text_format_new)
            worksheet.write(row, col + 3, emp.emp_code or '', cell_text_format_new)
            worksheet.write(row, col + 4, emp.name or '', cell_text_format_new)
            worksheet.write(row, col + 5, '', cell_text_format_new)
            worksheet.write(row, col + 6, '', cell_text_format_new)
            worksheet.write(row, col + 7, emp.gender.capitalize() if emp.gender else '', cell_text_format_new)
            worksheet.write(row, col + 8, emp.birthday or '', cell_date_format)
            worksheet.write(row, col + 9, '', cell_number_format)
            row += 1
            rec = relationship_data.filtered(lambda x: x.emp_name == emp)
            for index, record in enumerate(rec):
                # worksheet.write(row, col,     '', cell_text_format_new)
                # worksheet.write(row, col + 1, '', cell_text_format_new)
                worksheet.write(row, col + 5,
                                record.relationship_id.name.capitalize() if record.relationship_id.name else '',
                                cell_text_format_new)
                worksheet.write(row, col + 6, record.dependant_id or '', cell_text_format_new)
                worksheet.write(row, col + 7, record.gender.capitalize() if record.gender else '', cell_text_format_new)
                worksheet.write(row, col + 8, record.date_of_birth or '', cell_date_format)
                worksheet.write(row, col + 9, record.insurance_amount or '', cell_number_format)
                row += 1

        without_dependant = self.env['hr.employee.without.dependant.report'].sudo().search([])
        unique_emp = set(without_dependant.mapped('emp_name'))
        for emp in unique_emp:
            rec = without_dependant.filtered(lambda x: x.emp_name == emp)
            for index, record in enumerate(rec):
                worksheet.write(row, col, record.location.alias or '', cell_text_format_new)
                worksheet.write(row, col + 1, record.department.name or '', cell_text_format_new)
                worksheet.write(row, col + 2, record.job_id.name or '', cell_text_format_new)
                worksheet.write(row, col + 3, record.emp_code or '', cell_text_format_new)
                worksheet.write(row, col + 4, record.emp_name or '', cell_text_format_new)
                worksheet.write(row, col + 5, '', cell_text_format_new)
                worksheet.write(row, col + 6, '', cell_text_format_new)
                worksheet.write(row, col + 7, record.gender.capitalize() if record.gender else '', cell_text_format_new)
                worksheet.write(row, col + 8, record.dob or '', cell_date_format)
                worksheet.write(row, col + 9, '', cell_number_format)
                row += 1

        workbook.close()
        fp.seek(0)
        self.download_file = base64.b64encode(fp.read())
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/employee_family_insurance_report/%s/download_file/Employee Health Insurance with Dependant Details.xls?download=true' % (
                self.id)
        }
        
    def slugify(self, value):
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
        value = re.sub('[^\w\s-]', '', value).strip().lower()
        return re.sub('[-\s]+', '-', value)
