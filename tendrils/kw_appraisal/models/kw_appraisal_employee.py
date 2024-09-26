# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import  ValidationError


class kw_appraisal_employee(models.Model):
    _name = 'kw_appraisal_employee'
    _description = 'Appraisal employee'
    _rec_name    = 'kw_survey_id'

    employee_id = fields.Many2many('hr.employee', 'kw_appraisal_employee_rel', 'employee', string='Employees', required=True)
    kw_survey_id = fields.Many2one('survey.survey', string="Appraisal Form", required=True,domain=[('survey_type.code', '=', 'appr')])
    change_kra = fields.Boolean(string="Change KRA",default=False)
    change_compt = fields.Boolean(string="Change Competencies",default=False)
    department_id = fields.Many2one('hr.department',string="Department")
    division =fields.Many2one('hr.department',string="Division")
    job_id =fields.Many2one('hr.job',string="Designation")
    level_id = fields.Many2one('kw_grade_level', string='Level')
    

    @api.model
    def create(self, values):
        record = super(kw_appraisal_employee, self).create(values)
        if record:
            self.env.user.notify_success(message='Template assign successfully.')
        return record

    @api.constrains('employee_id')
    def no_employee_validate(self):
        for record in self:
            if not record.employee_id:
                raise ValidationError("Employee List should not be blank.")

    @api.multi
    def write(self, values):
        self.ensure_one()
        super(kw_appraisal_employee, self).write(values)
        self.env.user.notify_success(message='Assign Template updated successfully.')
        return True

    @api.multi
    def unlink(self):
        record = super(kw_appraisal_employee, self).unlink()
        if record:
            self.env.user.notify_success(message='Assign Template deleted successfully.')
        return record


    @api.multi
    @api.constrains('employee_id')
    def employee_validate(self):
        existing_record = self.env['kw_appraisal_employee'].sudo().search([])-self
        for record in self:
            emp_ids = record.employee_id.ids

            for records in existing_record:
                emp_ids_existing = records.employee_id.ids
                for items in emp_ids:
                    if items in emp_ids_existing:
                        raise ValidationError("Some employees may already tagged in other appraisal form")

    @api.multi
    @api.constrains('kw_survey_id')
    def survey_validate(self):
        s_id = self.env['kw_appraisal_employee'].sudo().search([])-self
        for record in s_id:
            survey_record = record.kw_survey_id.ids
            if self.kw_survey_id.id in survey_record:
                raise ValidationError("This Appraisal form already exists...")