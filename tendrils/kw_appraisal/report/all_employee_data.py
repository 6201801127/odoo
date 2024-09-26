from datetime import datetime,date
from odoo.tools.misc import format_date
from odoo import models, fields, api, tools, _
from io import BytesIO
import xlsxwriter
import unicodedata
import base64
import re
from xlsxwriter.utility import xl_rowcol_to_cell
import calendar
from dateutil.relativedelta import relativedelta

class KwEmployeeAllData(models.Model):
    _name           = "kw_emp_all_data"
    _description    = "Employee Details"
    _auto           = False

    department = fields.Char(string="Department")
    division = fields.Char(string="Division")
    section = fields.Char(string="Section")
    practise = fields.Char(string="Practise")
    budget_type = fields.Selection([('project', 'Project'), ('treasury', 'Treasury')], 'Budget Type')
    project = fields.Char(string="Project")
    date_of_joining = fields.Date(string="Date of Joining")
    emp_code = fields.Char(string="Emp Code")
    designation = fields.Char(string="Designation")
    reporting_authority = fields.Char(string="Reporting Authority")
    designation_of_ra = fields.Char(string="Designation of RA")
    upper_ra = fields.Char(string="Upper RA")
    upper_ra_designation = fields.Char(string="Upper RA Designation")
    name = fields.Char(string="Name")
    
    
    

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
            
        select row_number() over() as id, (select name from hr_department where id = a.department_id) as department,
        (select name from hr_department where id = a.division) as division,
(select name from hr_department where id = a.section) as section,
(select name from hr_department where id = a.practise) as practise,
budget_type,(select name from crm_lead where id =a.emp_project_id) as project,date_of_joining,
concat(split_part(emp_code::TEXT, '-', 1),'-',split_part(emp_code::TEXT, '-', 2)) as emp_code,
name,(select name from hr_job where id = a.job_id) as designation,(select name from hr_employee where id = a.parent_id) as reporting_authority,
(select name from hr_job where id = (select job_id from hr_employee where id = a.parent_id)) as designation_of_ra,
(select name from hr_employee where id = (select parent_id from hr_employee where id = a.parent_id)) as upper_ra,
(select name from hr_job where id = (select job_id from hr_employee where id = (select parent_id from hr_employee where id = a.parent_id))) as upper_ra_designation
from hr_employee a where active = true and a.employement_type != (select id from kwemp_employment_type where code='O')
                )""" % (self._table))
    
class DownloadEmployeeDetailsReport(models.TransientModel):
    _name = "employee_details_report_download"
    _description = "Employee Details Download Report"

    @api.model
    def default_get(self, fields):
        res = super(DownloadEmployeeDetailsReport, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])

        res.update({
            'appr_emp_details_ids': active_ids,
        })

        return res

    appr_emp_details_ids = fields.Many2many(
        string='Details',
        comodel_name='kw_emp_all_data',
        relation='emp_appraisal_download_rel',
        column1='appraisal_id',
        column2='download_id',
    )
    download_file = fields.Binary(string="Download Xls")

    @api.multi
    def download_emp_report(self):
        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        date_default_col1_style = workbook.add_format({ 'font_size': 12,  'align': 'center', 'num_format': 'yyyy-mm-dd'})
        date_default_col1_style.set_border()

        cell_text_format_n = workbook.add_format({'align': 'left', 'bold': False, 'size': 9, })
        cell_text_format_n.set_border()

        cell_text_center_normal = workbook.add_format({'align': 'center', 'bold': True, 'size': 11, })
        cell_text_center_normal.set_border()

        cell_text_format = workbook.add_format({'align': 'left', 'bold': False, 'size': 12, })
        cell_text_format.set_border()

        cell_text_amount_format =  workbook.add_format(
            {'align': 'right', 'bold': False, 'size': 9, 'num_format': '#,###0.00'})
        cell_text_amount_format.set_border()

        cell_total_amount_format =  workbook.add_format(
            {'align': 'center', 'bold': True, 'size': 9, 'num_format': '#,###0.00'})
        cell_total_amount_format.set_border()


        cell_number_total_format = workbook.add_format(
            {'align': 'center', 'bold': True, 'size': 9, 'num_format': '########'})
        cell_number_total_format.set_border()

        worksheet = workbook.add_worksheet(f'Employee Role and Category wise report')

        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:B', 30)
        worksheet.set_column('C:C', 30)
        worksheet.set_column('D:D', 30)
        worksheet.set_column('E:E', 30)
        worksheet.set_column('F:F', 30)
        worksheet.set_column('G:G', 30)
        worksheet.set_column('H:H', 30)
        worksheet.set_column('I:I', 30)
        worksheet.set_column('J:J', 30)
        worksheet.set_column('K:K', 30)
        worksheet.set_column('L:L', 30)
        worksheet.set_column('M:M', 30)
        worksheet.set_column('N:N', 30)


        row = 0
        worksheet.write(row, 0, 'Department', cell_text_center_normal)
        worksheet.write(row, 1, 'Division', cell_text_center_normal)
        worksheet.write(row, 2, 'Section', cell_text_center_normal)
        worksheet.write(row, 3, 'Practice', cell_text_center_normal)
        worksheet.write(row, 4, 'Budget Type', cell_text_center_normal)
        worksheet.write(row, 5, 'Project', cell_text_center_normal)
        worksheet.write(row, 6, 'Date of Joining', cell_text_center_normal)
        worksheet.write(row, 7, 'Emp Code', cell_text_center_normal)
        worksheet.write(row, 8, 'Name', cell_text_center_normal)
        worksheet.write(row, 9, 'Designation', cell_text_center_normal)
        worksheet.write(row, 10, 'Reporting Authority', cell_text_center_normal)
        worksheet.write(row, 11, 'Designation of RA', cell_text_center_normal)
        worksheet.write(row, 12, 'Upper RA', cell_text_center_normal)
        worksheet.write(row, 13, 'Upper RA Designation', cell_text_center_normal)


       
        row += 1
        col = 0


       
        for formb in self.appr_emp_details_ids:
            worksheet.write(row, col, formb.department or '', cell_text_format)
            worksheet.write(row, col + 1, formb.division or '', cell_text_format)
            worksheet.write(row, col + 2, formb.section or '', cell_text_format)
            worksheet.write(row, col + 3, formb.practise or '', cell_text_format)
            worksheet.write(row, col + 4, formb.budget_type or '', cell_text_format)
            worksheet.write(row, col + 5, formb.project or '', cell_text_format)
            worksheet.write(row, col + 6, formb.date_of_joining or '', date_default_col1_style)
            worksheet.write(row, col + 7, formb.emp_code or '', cell_text_format)
            worksheet.write(row, col + 8, formb.name or '', cell_text_format)
            worksheet.write(row, col + 9, formb.designation or '', cell_text_format)
            worksheet.write(row, col + 10, formb.reporting_authority or '', cell_text_format)
            worksheet.write(row, col + 11, formb.designation_of_ra or '', cell_text_format)
            worksheet.write(row, col + 12, formb.upper_ra or '', cell_text_format)
            worksheet.write(row, col + 13, formb.upper_ra_designation or '', cell_text_format)

            row += 1
      

        workbook.close()
        fp.seek(0)
        self.download_file = base64.b64encode(fp.read())
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/employee_details_report_download/%s/download_file/Employee Details.xls?download=true' % (
                self.id)
        }
        
    def slugify(self, value):
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
        value = re.sub('[^\w\s-]', '', value).strip().lower()
        return re.sub('[-\s]+', '-', value)
