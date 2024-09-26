# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re


class kw_skill_type(models.Model):
    _name = 'kw_skill_type_master'
    _description = "A model to create skill type master."
    _rec_name = 'skill_type'
    _order = 'skill_type'

    skill_type = fields.Char(string="Skill Type", required=True, size=100)
    # skill_type_description = fields.Text(string="Description", size=100)
    # soft_skill = fields.Boolean(string="Is soft skill?")
    active = fields.Boolean(string='Status', default=True,
                            help="The active field allows you to hide the test without removing it.")
    skill_code = fields.Char(string="Code")

    @api.constrains('skill_type', )
    def validate_skill_type_name(self):
        if re.match("^[a-zA-Z0-9 ,./()_+-]+$", self.skill_type) == None:
            raise ValidationError("Invalid Skill Type! Please provide a valid Skill Type")

        record = self.env['kw_skill_type_master'].search([]) - self
        for info in record:
            if info.skill_type.lower() == self.skill_type.lower():
                raise ValidationError("The Skill Type \"" + self.skill_type + "\" already exists.")

    @api.model
    def create(self, vals):
        new_record = super(kw_skill_type, self).create(vals)
        self.env.user.notify_success(message='Skill Type created successfully.')
        return new_record

    @api.multi
    def write(self, vals):
        res = super(kw_skill_type, self).write(vals)
        self.env.user.notify_success(message='Skill Type updated successfully.')
        return res

    @api.multi
    def unlink(self):
        for record in self:
            record.active = False
        return True
