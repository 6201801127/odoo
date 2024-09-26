# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re


class kw_skill_group_master(models.Model):
    _name = 'kw_skill_group_master'
    _description = "A master model to create Skill Groups."

    name = fields.Char(string="Name", required=True, size=100)
    description = fields.Char(string="Description", required=True, size=100)
    skills = fields.Many2many('kw_skill_master')
    active = fields.Boolean(string='Status', default=True,
                            help="The active field allows you to hide the test without removing it.")

    @api.constrains('name', )
    def validate_skill_name(self):
        if re.match("^[a-zA-Z0-9 ,./()_+-]+$", self.name) == None:
            raise ValidationError("Invalid Skill Group ! Please provide a valid Skill Group ")

        record = self.env['kw_skill_group_master'].search([]) - self
        for info in record:
            if info.name.lower() == self.name.lower():
                raise ValidationError("The Skill  \"" + self.name + "\" already exists.")

    @api.model
    def create(self, vals):
        new_record = super(kw_skill_group_master, self).create(vals)
        self.env.user.notify_success(message='Skill group created successfully.')
        return new_record

    @api.constrains('skills')
    def _check_skill(self):
        for record in self:
            if len(record.skills) < 1:
                raise ValidationError("Please add at least one skill.")

    @api.multi
    def write(self, vals):
        res = super(kw_skill_group_master, self).write(vals)
        self.env.user.notify_success(message='Skill group updated successfully.')
        return res

    @api.multi
    def unlink(self):
        for record in self:
            record.active = False
        return True
