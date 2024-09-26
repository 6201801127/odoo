from odoo import fields, models, api
from odoo.exceptions import ValidationError
import datetime,calendar
from datetime import date, datetime, time


class kw_payroll_zero_payslip(models.Model):
    _name = 'kw_payroll_zero_payslip'
    _description = 'Zero Payslip'
    # _rec_name = "display_name"

    MONTH_LIST = [
        ('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'),
        ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'),
        ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')
    ]

    @api.model
    def _get_year_list(self):
        current_year = date.today().year
        return [(str(i), i) for i in range(current_year, 1998, -1)]

    year = fields.Selection(string='Year', selection='_get_year_list', default=str(date.today().year))
    month = fields.Selection(MONTH_LIST, string='Month', default=str(date.today().month))
    employee = fields.Many2one('hr.employee', string="Employee",
                               domain="['|', ('active', '=', False), ('active', '=', True)]")
    department = fields.Char(related='employee.department_id.name', string="Department", store=True)
    division = fields.Char(related='employee.division.name', string="Division")
    section = fields.Char(related='employee.section.name', string="Section")
    practice = fields.Char(related='employee.practise.name', string="Practice")
    designation = fields.Char(related='employee.job_id.name', string="Designation")
    current_month = fields.Boolean(search="_search_current_month", compute='_compute_current_month')
    boolean_readonly = fields.Boolean(string='Printed In Payslip', default=False)
    reason = fields.Text(required=True)
    company_id = fields.Many2one('res.company')

    @api.onchange('year', 'month')
    def onchange_company(self):
        for rec in self:
            if rec.year and rec.month:
                emp_lst = []
                emp_rec = self.env['hr.employee']
                emp = emp_rec.sudo().search([('enable_payroll', '=', 'yes'), ('active', '=', True)])
                inactive_emp = emp_rec.sudo().search([('enable_payroll', '=', 'yes'), ('active', '=', False),('last_working_day','!=',False)])
                
                last_date = calendar.monthrange(int(rec.year), int(rec.month))[1]
                date_of_join = datetime(int(rec.year), int(rec.month), int(last_date))
                active_filter = emp.filtered(
                    lambda x: x.date_of_joining <= date_of_join.date())

                previous_month = datetime(int(rec.year), int(rec.month)-1, 26) if int(rec.month) != 1 else datetime(int(rec.year)-1,12, 26)
                previous_month_date = previous_month.date()
                inactive_filter = inactive_emp.filtered(
                    lambda x: x.last_working_day >= previous_month_date and x.date_of_joining <= date_of_join.date())
                for employee in active_filter:
                    emp_lst.append(employee.id)
                for employee in inactive_filter:
                    emp_lst.append(employee.id)
                return {
                    'domain': {'employee': [('id', 'in', emp_lst), '|', ('active', '=', False), ('active', '=', True)]}}

    @api.constrains('employee', 'year', 'month')
    def validate_zero_payslip(self):
        for rec in self:
            record = self.env['kw_payroll_zero_payslip'].sudo().search(
                [('year', '=', rec.year), ('month', '=', rec.month), ('employee', '=', rec.employee.id),
                 ]) - self
            if record:
                res = [item[1] for item in rec.MONTH_LIST if item[0] == record.month]
                month = res[0]
                raise ValidationError(
                    f"Duplicate entry found for {record.employee.emp_display_name} for {month}-{record.year}.")
    @api.multi
    def _compute_current_month(self):
        for record in self:
            pass

    @api.multi
    def _search_current_month(self, operator, value):
        month = date.today().month
        year = date.today().year
        return ['&', ('month', '=', str(month)), ('year', '=', str(year))]

    @api.onchange('employee_id')
    def change_contract(self):
        self.company_id = self.employee_id.company_id.id

                
    @api.model
    def create(self, vals):
        res = super(kw_payroll_zero_payslip, self).create(vals)
        ir_config_params = self.env['ir.config_parameter'].sudo()
        enable_zero_payslip = ir_config_params.get_param('payroll_inherit.enable_zero_payslip') or False
        if enable_zero_payslip != False:
            attendance_info = self.env['kw_payroll_monthly_attendance_report'].sudo().search(
            [('attendance_year', '=', int(res.year)), ('attendance_month', '=', int(res.month)),
             ('employee_id', '=', res.employee.id)])
            if attendance_info:
                attendance_info.sudo().write({'zero_payslip_boolean':True})
        return res
    
    @api.multi
    def unlink(self):
        for rec in self:
            attendance_info = self.env['kw_payroll_monthly_attendance_report'].sudo().search(
            [('attendance_year', '=', int(rec.year)), ('attendance_month', '=', int(rec.month)),
             ('employee_id', '=', rec.employee.id)])
            if attendance_info:
                attendance_info.sudo().write({'zero_payslip_boolean':False})
        return super(kw_payroll_zero_payslip, self).unlink()