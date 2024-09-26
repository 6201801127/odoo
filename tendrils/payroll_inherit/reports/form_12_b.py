from odoo import fields, models, _, api
from odoo import tools
from datetime import date, datetime, time
from odoo.addons import decimal_precision as dp
from io import BytesIO
import xlsxwriter
import unicodedata
import base64
import re
from xlsxwriter.utility import xl_rowcol_to_cell
import calendar
from dateutil.relativedelta import relativedelta


class PayrollForm12B(models.Model):
    _name = 'payroll_form_12_b'
    _description = 'Form 12 B Report'
    _auto = False

    MONTH_LIST = [
        ('1', 'January'), ('2', 'February'),
        ('3', 'March'), ('4', 'April'),
        ('5', 'May'), ('6', 'June'),
        ('7', 'July'), ('8', 'August'),
        ('9', 'September'), ('10', 'October'),
        ('11', 'November'), ('12', 'December')
    ]

    date_to=fields.Date(string="To Date")
    year = fields.Char(string="Year", size=4)
    month = fields.Selection(MONTH_LIST, string='Month', default=str(date.today().month))
    name = fields.Char(string="Employee Name",related='employee_id.name')
    emp_code = fields.Char(string='Employee Code',related='employee_id.emp_code')
    employee_id = fields.Many2one('hr.employee',string='Employee Name')
    month_name = fields.Char(compute='compute_month',string="Month")
    final_gross = fields.Float(string='Final Gross',digits=dp.get_precision('Payroll'))
    department = fields.Char(string='Department',related='employee_id.department_id.name')
    job = fields.Char(string='Designation',related='employee_id.job_id.name')
    current_month = fields.Boolean(search="_search_current_month", compute='_compute_current_month')

    @api.depends('month')
    def compute_month(self):
        month_dict = {'1': 'January', '2': 'February', '3': 'March', '4': 'April', '5': 'May', '6': 'June', '7': 'July', '8': 'August',
        '9': 'September', '10': 'October', '11': 'November', '12': 'December'}
        for rec in self:
            if rec.month:
                rec.month_name = month_dict.get(rec.month)
    @api.multi
    def _compute_current_month(self):
        for record in self:
            pass

    @api.multi
    def _search_current_month(self, operator, value):
        month = date.today().month
        year = date.today().year
        return ['&', ('month', '=', str(month)), ('year', '=', str(year))]
   
            
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as(
            select row_number() over() as id,
                date_part('year',a.date_to) as year,
                CAST(date_part('month',a.date_to) as varchar(10)) as month,
                a.date_to as date_to,
                sum(b.amount) FILTER (WHERE b.code = 'GROSS') as final_gross,
                a.employee_id as employee_id
                from hr_payslip a 
                join hr_payslip_line b
                on a.id = b.slip_id join hr_employee c on a.employee_id = c.id
                where b.code in ('GROSS') and b.amount > 0 and state='done'
                group by a.date_to,a.employee_id
			)""" % (self._table))

class PayrollForm12BVerify(models.Model):
    _name = 'payroll_form_12_b_verify'
    _description = 'Form 12 B Verify Report'
    _auto = False

    MONTH_LIST = [
        ('1', 'January'), ('2', 'February'),
        ('3', 'March'), ('4', 'April'),
        ('5', 'May'), ('6', 'June'),
        ('7', 'July'), ('8', 'August'),
        ('9', 'September'), ('10', 'October'),
        ('11', 'November'), ('12', 'December')
    ]

    date_to=fields.Date(string="To Date")
    year = fields.Char(string="Year", size=4)
    month = fields.Selection(MONTH_LIST, string='Month', default=str(date.today().month))
    name = fields.Char(string="Employee Name",related='employee_id.name')
    emp_code = fields.Char(string='Employee Code',related='employee_id.emp_code')
    employee_id = fields.Many2one('hr.employee',string='Employee Name')
    month_name = fields.Char(compute='compute_month',string="Month")
    final_gross = fields.Float(string='Final Gross',digits=dp.get_precision('Payroll'))
    department = fields.Char(string='Department',related='employee_id.department_id.name')
    job = fields.Char(string='Designation',related='employee_id.job_id.name')
    current_month = fields.Boolean(search="_search_current_month", compute='_compute_current_month')

    @api.depends('month')
    def compute_month(self):
        month_dict = {'1': 'January', '2': 'February', '3': 'March', '4': 'April', '5': 'May', '6': 'June', '7': 'July', '8': 'August',
        '9': 'September', '10': 'October', '11': 'November', '12': 'December'}
        for rec in self:
            if rec.month:
                rec.month_name = month_dict.get(rec.month)
    @api.multi
    def _compute_current_month(self):
        for record in self:
            pass

    @api.multi
    def _search_current_month(self, operator, value):
        month = date.today().month
        year = date.today().year
        return ['&', ('month', '=', str(month)), ('year', '=', str(year))]

    
            
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as(
            select row_number() over() as id,
            date_part('year',a.date_to) as year,
            CAST(date_part('month',a.date_to) as varchar(10)) as month,
            a.date_to as date_to,
            sum(b.amount) FILTER (WHERE b.code = 'GROSS') as final_gross,
            a.employee_id as employee_id
            from hr_payslip a 
            join hr_payslip_line b
            on a.id = b.slip_id join hr_employee c on a.employee_id = c.id
            where b.code in ('GROSS') and b.amount > 0
            group by a.date_to,a.employee_id)""" % (self._table))

class DownloadForm12BReport(models.TransientModel):
    _name = "form12b_report_download"
    _description = "Form 12B Download Report"

    @api.model
    def default_get(self, fields):
        res = super(DownloadForm12BReport, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])

        res.update({
            'formb_details_ids': active_ids,
        })

        return res

    formb_details_ids = fields.Many2many(
        string='Details',
        comodel_name='payroll_form_12_b',
        relation='form12b_download_rel',
        column1='formq2b_id',
        column2='download_id',
    )
    download_file = fields.Binary(string="Download Xls")

    @api.multi
    def download_form12b_report(self):
        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)

        cell_text_format_n = workbook.add_format({'align': 'left', 'bold': False, 'size': 9, })
        cell_text_format_n.set_border()

        cell_text_center_normal = workbook.add_format({'align': 'center', 'bold': True, 'size': 11, })
        cell_text_center_normal.set_border()

        cell_text_format = workbook.add_format({'align': 'left', 'bold': True, 'size': 11, })
        cell_text_format.set_border()

        cell_text_amount_format =  workbook.add_format(
            {'align': 'right', 'bold': False, 'size': 9, 'num_format': '#,###0.00'})
        cell_text_amount_format.set_border()

        cell_total_amount_format =  workbook.add_format(
            {'align': 'center', 'bold': True, 'size': 9, 'num_format': '#,###0.00'})
        cell_total_amount_format.set_border()

        cell_number_format = workbook.add_format(
            {'align': 'center', 'bold': False, 'size': 9, 'num_format': '########'})
        cell_number_format.set_border()

        cell_number_total_format = workbook.add_format(
            {'align': 'center', 'bold': True, 'size': 9, 'num_format': '########'})
        cell_number_total_format.set_border()

        worksheet = workbook.add_worksheet(f'Employee Role and Category wise report')

        worksheet.set_column('A:A', 10)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('E:E', 20)
        worksheet.set_column('F:F', 30)
        worksheet.set_column('G:G', 20)
        worksheet.set_column('H:H', 20)
        worksheet.set_column('I:I', 20)
       
        row = 0
        worksheet.write(row, 0, 'Year', cell_text_center_normal)
        worksheet.write(row, 1, 'Month', cell_text_center_normal)
        worksheet.write(row, 2, 'Department', cell_text_center_normal)
        worksheet.write(row, 3, 'Designation', cell_text_center_normal)
        worksheet.write(row, 4, 'Employee Code', cell_text_center_normal)
        worksheet.write(row, 5, 'Employee Name', cell_text_center_normal)
        worksheet.write(row, 6, 'Final Gross', cell_text_center_normal)
        row += 1
        col = 0
       
        for formb in self.formb_details_ids:
            worksheet.write(row, col, formb.year or '', cell_number_format)
            worksheet.write(row, col + 1, formb.month_name or '', cell_text_format_n)
            worksheet.write(row, col + 2, formb.department or '', cell_text_format_n)
            worksheet.write(row, col + 3, formb.job or '', cell_text_format_n)
            worksheet.write(row, col + 4, formb.emp_code or '', cell_number_format)
            worksheet.write(row, col + 5, formb.name or '', cell_text_format_n)
            worksheet.write(row, col + 6, formb.final_gross or '', cell_text_amount_format)
            row += 1
        gross = 0
        for line in self.formb_details_ids:
            gross += line.final_gross
            
            worksheet.write(row+1, col+6, gross, cell_total_amount_format)

        row += 1

        worksheet.write(row, 5, 'Total', cell_number_total_format)
        workbook.close()
        fp.seek(0)
        self.download_file = base64.b64encode(fp.read())
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/form12b_report_download/%s/download_file/Form 12-B Report.xls?download=true' % (
                self.id)
        }
        
    def slugify(self, value):
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
        value = re.sub('[^\w\s-]', '', value).strip().lower()
        return re.sub('[-\s]+', '-', value)

