from odoo import models, fields
from datetime import datetime
from odoo.exceptions import ValidationError


class SyncedKwantifySolutionsEmployee(models.Model):
    _name = 'synced_kwantify_solutions_employee'
    _description = 'Synchronized Kwantify Solutions Employee Data'

    kw_sol_emp_id = fields.Integer(string='Kw Sol. Employee Id')
    name = fields.Char(string='Name')
    department_name = fields.Char(string='Department Name')
    designation = fields.Char(string='Designation')
    work_location = fields.Char(string='Work Location')
    administrative_authority = fields.Char(string='Administrative Authority')
    email = fields.Char(string='Email')
    mobile_phone = fields.Char(string='Mobile Phone')
    date_of_joining = fields.Char(string='Date of Joining')
    employment_type = fields.Char(string='Employment Type')
    vendor_name = fields.Char(string='Vendor Name')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string='Gender')
    birthday = fields.Char(string='Birthday')
    current_ctc = fields.Float(string="Salary")
    active = fields.Boolean(string="Active")
    hr_employee_ref_id = fields.Many2one('hr.employee', string="Employee Ref.")


    def open_employee_creation_form(self):
        view_id = self.env.ref('kw_face_reader_integration.create_employee_wizard_form').id
        date_of_joining = datetime.strptime(self.date_of_joining, '%d-%m-%Y').date() if self.date_of_joining else False
        birthday = datetime.strptime(self.birthday, '%d-%m-%Y').date() if self.birthday else False
        return {
            'name': "Create Employee",
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'create_employee_wizard',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'current_id': self.id,
                'default_kw_sol_emp_id': self.kw_sol_emp_id,
                'default_name': self.name,
                'default_email': self.email,
                'default_mobile_phone': self.mobile_phone,
                'default_date_of_joining': date_of_joining,
                'default_gender': self.gender,
                'default_birthday': birthday,
                'default_current_ctc': self.current_ctc
            }
        }


class CreateEmployeeWizard(models.TransientModel):
    _name = 'create_employee_wizard'
    _description = 'Synchronized Kwantify Solutions Employee Data Create Wizard'

    ref_id = fields.Many2one('synced_kwantify_solutions_employee', default=lambda self: self.env.context.get('current_id'))
    kw_sol_emp_id = fields.Integer(string='Kw Sol. Employee Id')
    name = fields.Char(string='Name')
    department_id = fields.Many2one('hr.department', string='Department')
    job_id = fields.Many2one('hr.job', string='Designation')
    job_branch_id = fields.Many2one('kw_res_branch', string='Work Location')
    parent_id = fields.Many2one('hr.employee', string='Administrative Authority')
    email = fields.Char(string='Email')
    mobile_phone = fields.Char(string='Mobile Phone')
    date_of_joining = fields.Date(string='Date of Joining')
    employment_type = fields.Many2one('kwemp_employment_type', string='Employment Type')
    vendor_id = fields.Many2one('res.partner', string='Vendor Name')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string='Gender')
    birthday = fields.Date(string='Birthday')
    current_ctc = fields.Float(string="Salary")


    def create_employee(self):
        employee_data = {
            'name': self.name,
            'department_id': self.department_id.id,
            'job_id': self.job_id.id,
            'job_branch_id': self.job_branch_id.id,
            'parent_id': self.parent_id.id,
            'work_email': self.email,
            'mobile_phone': self.mobile_phone,
            'date_of_joining': self.date_of_joining,
            'employement_type': self.employment_type.id,
            'vendor_id': self.vendor_id.id,
            'gender': self.gender,
            'birthday': self.birthday,
            'current_ctc': self.current_ctc
        }
        
        created_employee = self.env['hr.employee'].create(employee_data)
        if created_employee:
            self.ref_id.hr_employee_ref_id = created_employee.id
        else:
            raise ValidationError("Not Created")