# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class kwemp_technical_category(models.Model):
    _name = 'kwemp_technical_category'
    _description = "Technical Categories"

    name = fields.Char(string="Category", required=True, size=100)
    skill_ids = fields.One2many('kwemp_technical_skill', 'category_id', required=True)
    kw_id = fields.Integer(string='Tendrils ID')
    active = fields.Boolean('Active', default=True)

    @api.constrains('name', )
    def validate_category(self):
        record = self.env['kwemp_technical_category'].search([]) - self
        for info in record:
            if info.name.lower() == self.name.lower():
                raise ValidationError("The category " + self.name + " already exists.")

    @api.model
    def create(self, vals):
        record = super(kwemp_technical_category, self).create(vals)
        if record:
            self.env.user.notify_success(message='Technical Categories Created successfully.')
        else:
            self.env.user.notify_danger(message='Technical Categories creation failed.')
        return record

    @api.multi
    def write(self, vals):
        res = super(kwemp_technical_category, self).write(vals)
        if res:
            self.env.user.notify_success(message='Technical Categories updated successfully.')
        else:
            self.env.user.notify_danger(message='Technical Categories updation failed.')
        return res


class kwemp_technical_skill(models.Model):
    _name = 'kwemp_technical_skill'
    _description = "Technical Skills"
    _order = "name"

    name = fields.Char(string="Skills", required=True, size=100)
    category_id = fields.Many2one('kwemp_technical_category', string="Category", required=True)
    kw_id = fields.Integer(string='Tendrils ID')

    @api.constrains('name', 'category_id')
    def validate_skill(self):
        record = self.env['kwemp_technical_skill'].search([]) - self
        for info in record:
            if (info.name.lower() == self.name.lower()) and (info.category_id == self.category_id):
                raise ValidationError("The skill " + self.name + " already exists.")

    @api.model
    def create(self, vals):
        record = super(kwemp_technical_skill, self).create(vals)
        if record:
            self.env.user.notify_success(message='Technical Skills Created successfully.')
        else:
            self.env.user.notify_danger(message='Technical Skills creation failed.')
        return record

    @api.multi
    def write(self, vals):
        res = super(kwemp_technical_skill, self).write(vals)
        if res:
            self.env.user.notify_info(message='Technical Skills updated successfully.')
        else:
            self.env.user.notify_danger(message='Technical Skills updation failed.')
        return res


class KwSkillMaster(models.Model):
    _name = 'kw_skill_master'
    _description = "A master model to create skills."
    _order = 'name'

    name = fields.Char(string="Name", required=True, size=100)
    description = fields.Text(string="Description")
    skill_type = fields.Many2one('kw_skill_type_master', string="Skill Category", required=True)
    # employee_id = fields.Many2many('hr.employee', string='Responsible Person')
    employee_id = fields.Many2many(
        comodel_name='hr.employee',
        relation='kw_skill_master_hr_employee_rel',
        string="Responsible Person",
        column1='skill_id',
        column2='emp_id')

    active = fields.Boolean(string='Status', default=True,
                            help="The active field allows you to hide the test without removing it.")
