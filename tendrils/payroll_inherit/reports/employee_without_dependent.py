from odoo import fields, models, api
from odoo import tools
from datetime import datetime, date, timedelta
from odoo.exceptions import UserError, ValidationError

class RecordBlockInsurance(models.Model):
    _name = 'hr_block_employee_in_self_ins'
    _description = 'Block Insurance'

    def _default_financial_yr(self):
        current_fiscal = self.env['account.fiscalyear'].search(
            [('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])
        return current_fiscal


    department = fields.Many2one("hr.department", string="Department",related='employee_id.department_id')
    job_id = fields.Many2one("hr.job", string="Designation",related='employee_id.job_id')
    emp_code = fields.Char(string="Employee Code",related='employee_id.emp_code')
    employee_id = fields.Many2one('hr.employee',string="Employee Name")
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('others', 'Others')],
                              string="Gender",related='employee_id.gender')
    dob = fields.Date(string="Date of Birth",related='employee_id.birthday')
    date_of_joining = fields.Date(related='employee_id.date_of_joining') 
    date_range = fields.Many2one('account.fiscalyear', 'Financial Year', track_visibility='always',
                                 default=_default_financial_yr)
    
    @api.constrains('employee_id', 'date_range')
    def submit_block_salary(self):
        for rec in self:
            blk_rec = self.env['hr_block_employee_in_self_ins'].sudo().search(
                [('employee_id', '=', rec.employee_id.id), ('date_range', '=', rec.date_range.id)]) - self
            if blk_rec:
                raise ValidationError(
                    f"{blk_rec.employee_id.name} is already blocked for this Financial Year")


class EmployeeNonDependant(models.Model):
    _name = "hr.employee.without.dependant.report"
    _description = "Report for without dependant Employee"
    _auto = False
    _order = "emp_name asc"

    location = fields.Many2one('kw_res_branch', 'Location')
    department = fields.Many2one("hr.department", string="Department")
    job_id = fields.Many2one("hr.job", string="Designation")
    emp_code = fields.Char(string="Employee Code")
    emp_name = fields.Char(string="Employee Name")
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('others', 'Others')],
                              string="Gender")
    dob = fields.Date(string="Date of Birth")
    gender = fields.Selection(selection=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], string='Gender',)
    date_of_joining = fields.Date()
    emp_active = fields.Boolean()


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        current_fiscal = self.env['account.fiscalyear'].search(
            [('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])
        query = f"""CREATE or REPLACE VIEW {self._table} as (
                    SELECT
                        em.id AS id,
                        em.job_branch_id AS location,
                        em.department_id AS department,
                        em.job_id AS job_id,
                        em.emp_code AS emp_code,
                        em.name AS emp_name,
                        em.birthday AS dob,
                        em.gender AS gender,
                        em.date_of_joining AS date_of_joining,
                        em.active AS emp_active
                    FROM
                        hr_employee AS em
                    LEFT JOIN health_insurance_dependant hd ON hd.employee_id = em.id AND hd.date_range =  {current_fiscal.id} and hd.state != 'rejected' 
                    WHERE
                        em.employement_type IN (SELECT id FROM kwemp_employment_type WHERE code NOT IN ('O', 'CE')) AND
                        em.esi_applicable IS FALSE AND
                        em.is_consolidated IS FALSE AND
                        hd.id IS NULL AND
                        em.id NOT IN (SELECT employee_id
                        FROM hr_block_employee_in_self_ins
                        WHERE date_range = {current_fiscal.id}) 
                    ORDER BY
                        em.name ASC
                            )"""
        self.env.cr.execute(query)

