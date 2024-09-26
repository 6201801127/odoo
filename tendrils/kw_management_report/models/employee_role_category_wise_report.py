from odoo import tools
from odoo import models, fields, api
from datetime import datetime,date
from odoo.addons import decimal_precision as dp

from io import BytesIO
import xlsxwriter
import unicodedata
import base64
import re
from xlsxwriter.utility import xl_rowcol_to_cell
import calendar
from dateutil.relativedelta import relativedelta



class KwAppraisalPageWiseReport(models.Model):
    _name           = "employee_role_catagory_wise_report"
    _description  = "Employee Role and Category wise report"
    _auto             = False


    def get_row(self):
        count=0
        for record in self:
            record.sl_no = count + 1
            count = count + 1

    financial_year= fields.Char(string='Financial Year')
    emp_role= fields.Char(string="Employee Role")
    emp_category= fields.Char(string="Employee Category")
    total_present= fields.Integer(string='Employee Count')
    total_ctc= fields.Integer(digits=dp.get_precision('Payroll'),string="Cumulative CTC drawn in the CFY")
    sl_no=fields.Integer("SL#",compute="get_row")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(""" CREATE or REPLACE VIEW %s as (
            select row_number() over(order by  (select name from kwmaster_role_name where id = c.emp_role) asc,(select name from kwmaster_category_name where id = c.emp_category) asc) as id,
            TO_DATE(
                CASE 
            WHEN date_part('month',date_to) <= 3 
            THEN concat(cast(date_part('year',date_to)-1 as varchar(4)),'-04-01')
            ELSE concat(cast(date_part('year',date_to) as varchar(4)),'-04-01') END,'YYYY-MM-DD') as start_date,
            TO_DATE(
                CASE 
            WHEN date_part('month',date_to) <= 3 
            THEN concat(cast(date_part('year',date_to) as varchar(4)),'-03-31')
            ELSE concat(cast(date_part('year',date_to)+1 as varchar(4)),'-03-31') END,'YYYY-MM-DD') as end_date,

            CASE 
            WHEN date_part('month',date_to) <= 3 
            THEN concat(cast(date_part('year',date_to)-1 as varchar(4)),'-',cast(date_part('year',date_to) as varchar(4)))
            ELSE concat(cast(date_part('year',date_to) as varchar(4)),'-',cast(date_part('year',date_to)+1 as varchar(4))) END as financial_year,
            (select name from kwmaster_role_name where id = c.emp_role) as emp_role,
            (select name from kwmaster_category_name where id = c.emp_category) as emp_category,
            count(DISTINCT C.id)  as total_present,
            sum(a.amount) as total_ctc
            from hr_payslip_line a join hr_payslip b on a.slip_id = b.id 
            join hr_employee c on b.employee_id = c.id 
            where a.code = 'CTC' and b.state = 'done'  and b.company_id = 1
            group by CASE WHEN date_part('month',date_to)<= 3 THEN concat(cast(date_part('year',date_to)-1 as varchar(4)),'-',cast(date_part('year',date_to) as varchar(4)))
                            ELSE concat(cast(date_part('year',date_to) as varchar(4)),'-',cast(date_part('year',date_to)+1 as varchar(4))) END,
                            TO_DATE(
                CASE 
            WHEN date_part('month',date_to) <= 3 
            THEN concat(cast(date_part('year',date_to)-1 as varchar(4)),'-04-01')
            ELSE concat(cast(date_part('year',date_to) as varchar(4)),'-04-01') END,'YYYY-MM-DD'),
            TO_DATE(
                CASE 
            WHEN date_part('month',date_to) <= 3 
            THEN concat(cast(date_part('year',date_to) as varchar(4)),'-03-31')
            ELSE concat(cast(date_part('year',date_to)+1 as varchar(4)),'-03-31') END,'YYYY-MM-DD'),
                c.emp_role,c.emp_category
          
        )""" % (self._table))


class DownloadRoleCategoryReport(models.TransientModel):
    _name = "employee_role_catagory_download"
    _description = "Download Report"

    @api.model
    def default_get(self, fields):
        res = super(DownloadRoleCategoryReport, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])

        res.update({
            'report_details_ids': active_ids,
        })

        return res

    report_details_ids = fields.Many2many(
        string='Details',
        comodel_name='employee_role_catagory_wise_report',
        relation='role_category_download_rel',
        column1='report_id',
        column2='download_id',
    )
    download_file = fields.Binary(string="Download Xls")

    @api.multi
    def download_role_report(self):
        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)


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
        cell_total_amount_format =  workbook.add_format(
            {'align': 'right', 'bold': True, 'size': 9, 'num_format': '#,###0.00'})
        cell_total_amount_format.set_border()
        cell_number_format = workbook.add_format(
            {'align': 'center', 'bold': False, 'size': 9, 'num_format': '########'})
        cell_number_format.set_border()
        cell_number_total_format = workbook.add_format(
            {'align': 'center', 'bold': True, 'size': 9, 'num_format': '########'})
        cell_number_total_format.set_border()

        # cell_date_format = workbook.add_format({'num_format': 'dd-mmm-yyyy', 'size': 9, })
        # cell_date_format.set_border()

        worksheet = workbook.add_worksheet(f'Employee Role and Category wise report')

        worksheet.set_column('A:A', 10)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('E:E', 40)
        worksheet.set_column('F:F', 20)
        worksheet.set_column('G:G', 20)
        worksheet.set_column('H:H', 20)
        worksheet.set_column('I:I', 20)
       
        row = 0
        worksheet.write(row, 0, 'SL #', cell_text_center_normal)
        worksheet.write(row, 1, 'Employee Role', cell_text_center_normal)
        worksheet.write(row, 2, 'Employee Category', cell_text_center_normal)
        worksheet.write(row, 3, 'Employee Count', cell_text_center_normal)
        worksheet.write(row, 4, 'Cumulative CTC drawn in the CFY', cell_text_center_normal)
        row += 1
        col = 0
       
        for emp in self.report_details_ids:
            worksheet.write(row, col, emp.sl_no or '', cell_number_format)
            worksheet.write(row, col + 1, emp.emp_role or '', cell_text_format_n)
            worksheet.write(row, col + 2, emp.emp_category or '', cell_text_format_n)
            worksheet.write(row, col + 3, emp.total_present or '', cell_number_format)
            worksheet.write(row, col + 4, emp.total_ctc or '', cell_text_amount_format)
            row += 1
        emp,ctc = 0,0
        for line in self.report_details_ids:
            emp += line.total_present
            ctc += line.total_ctc

            worksheet.write(row, col+3, emp, cell_number_total_format)
            worksheet.write(row, col+4, ctc, cell_total_amount_format)

        row += 1

        worksheet.write(row-1, 2, 'Total', cell_text_center_normal)
        workbook.close()
        fp.seek(0)
        self.download_file = base64.b64encode(fp.read())
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/employee_role_catagory_download/%s/download_file/Report.xls?download=true' % (
                self.id)
        }
        
    def slugify(self, value):
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
        value = re.sub('[^\w\s-]', '', value).strip().lower()
        return re.sub('[-\s]+', '-', value)

    
  
   