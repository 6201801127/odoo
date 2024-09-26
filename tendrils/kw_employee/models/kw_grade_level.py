# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class kw_grade_level(models.Model):
    _name = 'kw_grade_level'
    _description = "Employee Grade Level Information"

    name = fields.Char(string="Level")
    grade_ids = fields.Many2many('kwemp_grade_master', 'kw_emp_grade_master_level_rel', 'level_id', 'grade_id',
                                 string='Grade')
    parent_id = fields.Many2one('kw_grade_level', string='Parent Level')
    status = fields.Boolean(string='Status', default=True)
    prof_persuit = fields.Float(string="Professional Pursuit")
    lta = fields.Float(string="LTA (Leave Travel Allowance)")

    @api.constrains('grade_ids')
    def validate_grade(self):
        record = self.env['kw_grade_level'].sudo().search([]) - self
        for info in record:
            if info.name.lower() == self.name.lower():
                raise ValidationError(f"The name {self.name} is already exists.")
            for rec in self.grade_ids.ids:
                if rec in info.grade_ids.ids:
                    raise ValidationError("This Grade is already exists.")

    @api.model
    def create(self, vals):
        record = super(kw_grade_level, self).create(vals)
        if record:
            self.env.user.notify_success(message='"Employee Grade Level created successfully.')
        else:
            self.env.user.notify_danger(message='"Employee Grade Level creation failed.')
        return record

    @api.multi
    def write(self, vals):
        res = super(kw_grade_level, self).write(vals)
        if res:
            self.env.user.notify_success(message='Employee Grade Level updated successfully.')
        else:
            self.env.user.notify_danger(message='Employee Grade Level updation failed.')
        return res

    def hr_employee_level_update_scheduler(self):
        employee_rec = self.env['hr.employee'].search([('level', '=', False), '|', ('active', '=', True), ('active', '=', False)])
        level_rec = self.env['kw_grade_level'].search([])
        if employee_rec.exists():
            update_list = []
            for rec in employee_rec:
                if rec.grade:
                    emp_level = level_rec.filtered(lambda x: rec.grade in x.grade_ids)
                    # print("emp_level >>> ", rec.name, emp_level)
                    if emp_level.exists():
                        update_list.append(f'UPDATE hr_employee SET level={emp_level.id} WHERE id={rec.id};')
                        # rec.write({
                        #     'level': emp_level.id
                        # })
            if update_list:
                exe_query = ''.join(update_list)
                query = self.env.cr.execute(exe_query)
