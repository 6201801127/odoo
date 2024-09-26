# -*- coding: utf-8 -*-

from odoo import models, fields, api, http
from odoo.exceptions import ValidationError


class kwemp_grade(models.Model):
    _name = 'kwemp_grade'
    _description = "Employment Grades"
    _order = "sort_no asc"

    name = fields.Char(string="Grade", size=100)
    description = fields.Text(string="Description", )
    kw_id = fields.Integer(string='Tendrils ID')
    grade_id = fields.Many2one('kwemp_grade_master', string='Grade')
    band_id = fields.Many2one('kwemp_band_master', string='Band')
    sort_no = fields.Integer(string="Sort No.")
    active = fields.Boolean('Active', default=True)

    @api.constrains('name', )
    def validate_organization_type(self):
        record = self.env['kwemp_grade'].search([]) - self
        for info in record:
            if info.name.lower() == self.name.lower():
                raise ValidationError("The grade \"" + self.name + "\" already exists.")

    @api.model
    def create(self, vals):
        if vals.get('grade_id'):
            grade = self.env['kwemp_grade_master'].search([('id', '=', vals.get('grade_id'))]).name
            if grade:
                vals['name'] = grade
        if vals.get('band_id'):
            band = self.env['kwemp_band_master'].search([('id', '=', vals.get('band_id'))]).name
            if vals.get('name'):
                vals['name'] = vals.get('name') + '-' + band
            else:
                vals['name'] = band
        record = super(kwemp_grade, self).create(vals)
        if record:
            self.env.user.notify_success(message='Employee Grade created successfully.')
        else:
            self.env.user.notify_danger(message='Employee Grade creation failed.')
        return record

    @api.multi
    def write(self, vals):
        res = super(kwemp_grade, self).write(vals)
        if res:
            self.env.user.notify_success(message='Employee Grade updated successfully.')
        else:
            self.env.user.notify_danger(message='Employee Grade updation failed.')
        return res
    
    _sql_constraints = [('name_uniq', 'unique (name)',
                         'Duplicate names not allowed.!')]
