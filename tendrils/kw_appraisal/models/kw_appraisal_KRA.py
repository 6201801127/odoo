from odoo import models, fields, api
from odoo.exceptions import  ValidationError


class kw_appraisal_KRA(models.Model):
    _name           = 'kw_appraisal_kra'
    _description    = 'Appraisal KRA'
    _rec_name       = 'employee_id'
    appraisal_period    = fields.Many2one('kw_assessment_period_master',string='Appraisal Period',)
    employee_id         = fields.Many2one('hr.employee',string='Employee')
    total_score         = fields.Integer('Total Score',default=100)
    actual_score        = fields.Float('Actual Score')
    achievement         = fields.Char('Achievement')
    
    
class Appraisal_Ratio(models.Model):
    _name           = 'kw_appraisal_ratio'
    _description    = "Appraisal Ratio Configuration"
    _rec_name       = 'department'

    department      = fields.Many2one(comodel_name='hr.department', string="Department")
    dep_emp         = fields.Many2many('hr.employee','hr_emp_dep_rel',string='Department Employees',compute='filter_dept_employee')
    
    division        = fields.Many2one(comodel_name='hr.department', string="Division")    
    section         = fields.Many2one(comodel_name='hr.department', string="Practice")    
    practice        = fields.Many2one(comodel_name='hr.department', string="Section")    
    per_appraisal   = fields.Integer(string='Appraisal Percentage')
    per_kra         = fields.Integer(string='KRA Percentage')
    per_inc         = fields.Integer(string='Increment Percentage')
    count_emp       = fields.Integer(compute='_count_employees',string='No. of Employees')
    
    @api.multi
    def _count_employees(self):
        for record in self:
            record.count_emp = len(record.dep_emp) if record.dep_emp else 0

    # @api.onchange('per_appraisal','per_kra')
    # def _validate_total(self):
    #     for record in self:
    #         if (record.per_appraisal > 0 and record.per_kra > 0) and (record.per_appraisal + record.per_kra) != 100:
    #             raise ValidationError("Sum of Appraisal Pecentage and KRA Percentage must be 100.")

    @api.constrains('per_appraisal','per_kra')
    def _validate_total(self):
        for record in self:
            if (record.per_appraisal + record.per_kra) != 100:
                raise ValidationError("Sum of Appraisal Pecentage and KRA Percentage must be 100.")

    
    @api.depends('department')
    def filter_dept_employee(self):
        for record in self:
            record.dep_emp = False
            if record.department:
                
                domain = [
                    ('department_id','=',record.department.id if record.department else False),
                    ('division','=',record.division.id if record.division else False),
                    ('section','=',record.section.id if record.section else False),
                    ('practise','=',record.practice.id if record.practice else False)
                    
                ]
                
                period_master = self.env['kw_assessment_period_master'].search([],order='id desc')
                appraisal_record = self.env['hr.appraisal'].search([('appraisal_year_rel','=',period_master[0].id or False)])
                enrolled_emp = appraisal_record.mapped('emp_id')
                if enrolled_emp:
                    domain += [('id','in',enrolled_emp.ids)]
                    
                employee_records = self.env['hr.employee'].search(domain)
                record.dep_emp = [(4, emp.id) for emp in employee_records]
            else:
                pass