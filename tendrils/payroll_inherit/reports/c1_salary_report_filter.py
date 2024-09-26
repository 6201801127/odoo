from odoo import fields, models, _, api
from odoo import tools
from datetime import date, datetime, time
import calendar
from odoo.exceptions import ValidationError, UserError


class C1SalaryReportFilter(models.TransientModel):
    _name = 'c1_salary_report_filter'
    _description = 'C1 Compiled Salary Report Filter'

    MONTH_LIST = [

        ('1', 'January'), ('2', 'February'),
        ('3', 'March'), ('4', 'April'),
        ('5', 'May'), ('6', 'June'),
        ('7', 'July'), ('8', 'August'),
        ('9', 'September'), ('10', 'October'),
        ('11', 'November'), ('12', 'December')
    ]

    year_data = fields.Selection(string='Year', selection='_get_year_list', default=str(date.today().year))
    month_data = fields.Selection(MONTH_LIST, string='Month', default=str(date.today().month))
    confirmed_on = fields.Date()

   

    @api.model
    def _get_year_list(self):
        current_year = date.today().year
        return [(str(i), i) for i in range(current_year + 7, 2010, -1)]

    def compute_verified_date(self):
        if self.year_data and self.month_data:
            batch_payslips = self.env['hr.payslip.run'].sudo().search([])
            batch = batch_payslips.filtered(lambda x:x.date_end.year ==int(self.year_data) and x.date_end.month == int(self.month_data))
            last_rec = batch_payslips.sudo().search([('id','in',batch.ids)],order='create_date desc',limit=1)
            if len(last_rec) == 1:
                self.confirmed_on = last_rec.confirmed_on

    def btn_show_c1_report(self):
        self.compute_verified_date()
        ir_config_params = self.env['ir.config_parameter'].sudo()
        company = ir_config_params.get_param('tds.tds_company_id') or False
        self.env['payroll_salary_compiled_report'].with_context(year_data=self.year_data,month_data= self.month_data,company=int(company)).init()
        view_id = self.env.ref('payroll_inherit.compiled_salary_report_view_tree').id
        name = f'C1 Report for {calendar.month_name[int(self.month_data)]}-{self.year_data}, Confirmed on : {self.confirmed_on.strftime("%d-%b-%Y")}' if self.confirmed_on else f'C1 Report for {calendar.month_name[int(self.month_data)]}-{self.year_data}'
        return {
            'name':name,
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(view_id, 'tree')],
            'res_model': 'payroll_salary_compiled_report',
            'view_id': view_id,
            'context': {'year_data':self.year_data,'month_data': self.month_data},
            'target': 'current',
        }
   

    def btn_show_c1_verified_report(self):
        self.compute_verified_date()
        ir_config_params = self.env['ir.config_parameter'].sudo()
        company = ir_config_params.get_param('tds.tds_company_id') or False
        self.env['c1_salary_verified_report'].with_context(year_data=self.year_data,month_data= self.month_data,company=int(company)).init()
        view_id = self.env.ref('payroll_inherit.c1_salary_verified_report_tree').id
        name = f'C1 Report for {calendar.month_name[int(self.month_data)]}-{self.year_data}, Confirmed on : {self.confirmed_on.strftime("%d-%b-%Y")}' if self.confirmed_on else f'C1 Report for {calendar.month_name[int(self.month_data)]}-{self.year_data}'
        return {
            'name': name,
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(view_id, 'tree')],
            'res_model': 'c1_salary_verified_report',
            'view_id': view_id,
            'context': {'year_data':self.year_data,'month_data': self.month_data},
            'target': 'current',
        }

    def btn_show_csmpl_verified_report(self):
        self.compute_verified_date()
        ir_config_params = self.env['ir.config_parameter'].sudo()
        company = ir_config_params.get_param('tds.tds_company_id') or False
        self.env['csmpl_salary_verified_report'].with_context(year_data=self.year_data,month_data= self.month_data,company=int(company)).init()
        view_id = self.env.ref('payroll_inherit.csmpl_salary_verified_report_view_tree').id
        name = f'CSMPL Report for {calendar.month_name[int(self.month_data)]}-{self.year_data}, Confirmed on : {self.confirmed_on.strftime("%d-%b-%Y")}' if self.confirmed_on else f'CSMPL Report for {calendar.month_name[int(self.month_data)]}-{self.year_data}'
        action = {
            'name':name,
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(view_id, 'tree')],
            'res_model': 'csmpl_salary_verified_report',
            'view_id': view_id,
            'target': 'current',
        }
        return action

    def btn_show_csmpl_report(self):
        self.compute_verified_date()
        ir_config_params = self.env['ir.config_parameter'].sudo()
        company = ir_config_params.get_param('tds.tds_company_id') or False
        self.env['csmpl_salary_compiled_report'].with_context(year_data=self.year_data,month_data= self.month_data,company=int(company)).init()
        view_id = self.env.ref('payroll_inherit.csmpl_salary_compiled_report_view_tree').id
        name = f'CSMPL Report for {calendar.month_name[int(self.month_data)]}-{self.year_data}, Confirmed on : {self.confirmed_on.strftime("%d-%b-%Y")}' if self.confirmed_on else f'CSMPL Report for {calendar.month_name[int(self.month_data)]}-{self.year_data}'
        action = {
            'name':name,
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(view_id, 'tree')],
            'res_model': 'csmpl_salary_compiled_report',
            'view_id': view_id,
            'target': 'current',
        }
        return action

class BatchWiseFilter(models.TransientModel):
    _name = 'batch_salary_report_filter'
    _description = 'Batch Compiled Salary Report Filter'

    MONTH_LIST = [

        ('1', 'January'), ('2', 'February'),
        ('3', 'March'), ('4', 'April'),
        ('5', 'May'), ('6', 'June'),
        ('7', 'July'), ('8', 'August'),
        ('9', 'September'), ('10', 'October'),
        ('11', 'November'), ('12', 'December')
    ]

    year_data = fields.Selection(string='Year', selection='_get_year_list', default=str(date.today().year))
    month_data = fields.Selection(MONTH_LIST, string='Month', default=str(date.today().month))
    confirmed_on = fields.Date()
    batch_id  = fields.Many2one('hr.payslip.run')
    
    @api.model
    def _get_year_list(self):
        current_year = date.today().year
        return [(str(i), i) for i in range(current_year + 7, 2010, -1)]

    def compute_verified_date(self):
        if self.year_data and self.month_data and self.batch_id:
            batch_payslip = self.env['hr.payslip.run'].sudo().browse(self.batch_id.id)
            if len(batch_payslip) == 1:
                self.confirmed_on = batch_payslip.confirmed_on

    @api.onchange('year_data','month_data')
    def populate_betch(self):
        if self.year_data and self.month_data:
            batch_payslips = self.env['hr.payslip.run'].sudo().search([])
            batch = batch_payslips.filtered(lambda x:x.date_end.year ==int(self.year_data) and x.date_end.month == int(self.month_data))
            if batch:
                if self.env.user.has_group('kw_employee.group_payroll_manager'):
                    return {'domain': {'batch_id': [('id', 'in', batch.ids)]}}
                if self.env.user.has_group('payroll_inherit.payroll_finance_group'):
                    rebatch = batch.filtered(lambda x:x.state=='confirm')
                    return {'domain': {'batch_id': [('id', 'in', rebatch.ids)]}}

    def btn_show_draft_report(self):
        self.compute_verified_date()
        ir_config_params = self.env['ir.config_parameter'].sudo()
        company = ir_config_params.get_param('tds.tds_company_id') or False
        self.env['batch_wise_bulk_report'].with_context(year_data=self.year_data,month_data= self.month_data,company=int(company),payslip_run_id = self.batch_id.id).init()
        view_id = self.env.ref('payroll_inherit.batch_wise_bulk_report_tree').id
        name = f'{self.batch_id.name} Report for {calendar.month_name[int(self.month_data)]}-{self.year_data}, Confirmed on : {self.confirmed_on.strftime("%d-%b-%Y")}' if self.confirmed_on else f'{self.batch_id.name} Report for {calendar.month_name[int(self.month_data)]}-{self.year_data}'
        return {
            'name':name,
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(view_id, 'tree')],
            'res_model': 'batch_wise_bulk_report',
            'view_id': view_id,
            'target': 'current',
        }
        
    def btn_show_verified_report(self):
        self.compute_verified_date()
        ir_config_params = self.env['ir.config_parameter'].sudo()
        company = ir_config_params.get_param('tds.tds_company_id') or False
        self.env['batch_wise_bulk_verified_report'].with_context(year_data=self.year_data,month_data= self.month_data,company=int(company),payslip_run_id = self.batch_id.id).init()
        view_id = self.env.ref('payroll_inherit.batch_wise_bulk_verified_report_view_tree').id
        name = f'{self.batch_id.name} Report for {calendar.month_name[int(self.month_data)]}-{self.year_data}, Confirmed on : {self.confirmed_on.strftime("%d-%b-%Y")}' if self.confirmed_on else f'{self.batch_id.name} Report for {calendar.month_name[int(self.month_data)]}-{self.year_data}'
        return {
            'name':name,
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(view_id, 'tree')],
            'res_model': 'batch_wise_bulk_verified_report',
            'view_id': view_id,
            'target': 'current',
        }
    

class GHIReport(models.TransientModel):
    _name = 'ghi_report'
    _description = 'GHI Report'

    fiscalyr = fields.Many2one('account.fiscalyear', string="Fiscal Year")
    from_date = fields.Date()
    to_date = fields.Date()


    def btn_show_ghi_report(self):
        self.env['payroll_ghi_details_report'].with_context(insurance_year=self.fiscalyr.id,from_date = self.from_date,date_to = self.to_date).init()
        view_id = self.env.ref('payroll_inherit.payroll_ghi_details_report_view_tree').id
        return {
            'name':'GHI Details',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(view_id, 'tree')],
            'res_model': 'payroll_ghi_details_report',
            'view_id': view_id,
            'target': 'current',
        }
        
    def btn_show_employee_details(self):
        self.env['personal_international_insurance'].with_context(from_date = self.from_date,date_to = self.to_date).init()
        view_id = self.env.ref('payroll_inherit.personal_international_insurance_view_tree').id
        return {
            'name':'Personal/International Insurance',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(view_id, 'tree')],
            'res_model': 'personal_international_insurance',
            'view_id': view_id,
            'target': 'current',
        }
class PersonalInternationalInsurance(models.Model):
    _name = 'personal_international_insurance'
    _description = 'insurance Report'
    _auto = False
    
    emp_code = fields.Char(string='')
    name = fields.Char(string='')
    employement_type = fields.Many2one('kwemp_employment_type', ondelete='cascade', string="Type of Employment")#16
    personal_insurance = fields.Selection([('Yes','Yes'),('No','No')],string="Health Insurance")
    insurance_validate_date = fields.Date(string='')
    employee_id = fields.Many2one('hr.employee')
    base_branch_id = fields.Many2one('kw_res_branch')
    department_id = fields.Many2one('hr.department')
    
    @api.model_cr
    def init(self):
        date_from = self.env.context.get('from_date') or date.today().strftime('%Y-%m-%d')
        date_to = self.env.context.get('date_to') or date.today().strftime('%Y-%m-%d')
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""
        CREATE OR REPLACE VIEW {self._table} AS (
            SELECT 
                id AS id,
                id AS employee_id,
                emp_code,
                name,
                employement_type,
                personal_insurance,
                insurance_validate_date,
                base_branch_id,
                department_id
            FROM hr_employee
            WHERE 
                (
                    (date_of_joining <= '{date_from}' AND last_working_day IS NULL AND active = true)
                    OR (date_of_joining BETWEEN '{date_from}' AND '{date_to}')
                    OR (last_working_day > '{date_from}' AND date_of_joining <= '{date_from}' AND active = false)
                    OR (last_working_day BETWEEN '{date_from}' AND '{date_to}' AND date_of_joining BETWEEN '{date_from}' AND '{date_to}' AND active = false)
                )
                AND department_id = (select id from hr_department where code='OFFS')
            UNION ALL
            SELECT 
                id AS id,
                id AS employee_id,
                emp_code,
                name,
                employement_type,
                personal_insurance,
                insurance_validate_date,
                base_branch_id,
                department_id
            FROM hr_employee
            WHERE 
                (
                    (date_of_joining <= '{date_from}' AND last_working_day IS NULL AND active = true)
                    OR (date_of_joining BETWEEN '{date_from}' AND '{date_to}')
                    OR (last_working_day > '{date_from}' AND date_of_joining <= '{date_from}' AND active = false)
                    OR (last_working_day BETWEEN '{date_from}' AND '{date_to}' AND date_of_joining BETWEEN '{date_from}' AND '{date_to}' AND active = false)
                )
                AND company_id != 1
        )
    """)

    def action_update_insurance(self):
        view_id = self.env.ref('payroll_inherit.update_employee_details_view_form').id
        return {
            'name':'Personal/International Insurance',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'res_model': 'update_employee_details',
            'view_id': view_id,
            'target': 'new',
            'context': {'employee_id':self.employee_id.id}
        }
class UpdateEmployeeInsurance(models.TransientModel):
    _name = 'update_employee_details'
    _description = 'Update Insurance Report'
    
    employee_id = fields.Many2one('hr.employee',default=lambda self: self.env.context.get('employee_id'))
    personal_insurance = fields.Selection([('Yes','Yes'),('No','No')],string="Health Insurance")
    insurance_validate_date = fields.Date(string='')
    insurance_doc = fields.Binary(string='Insurance Document',attachment=True)
    file_name_insurance = fields.Char(string="File Name") 
    
    @api.onchange('personal_insurance')
    def change_date(self):
        if self.personal_insurance == 'No':
            self.insurance_validate_date = False
            self.insurance_doc = False
            
    def update_employee_detail(self):
        if self.employee_id and  self.personal_insurance in ('Yes','No'):
                self.employee_id.uplod_insurance_doc = self.insurance_doc
                self.employee_id.file_name_insurance = self.file_name_insurance
                self.employee_id.insurance_validate_date = self.insurance_validate_date
                self.employee_id.personal_insurance = self.personal_insurance
        else:
            raise ValidationError('Please update the details')
            
    