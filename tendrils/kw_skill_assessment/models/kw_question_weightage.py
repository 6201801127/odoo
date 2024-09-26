import re

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class kw_Question_Weightage(models.Model):
    _name = 'kw_skill_question_weightage'
    _description = "A model to create Questions weightage"

    name = fields.Char(string="Weightage Name", required=True, size=100)
    code = fields.Char('Code')
    weightage = fields.Integer(string="Weightage", default='1', required=True)
    duration = fields.Integer(string="Duration", default='1', required=True)
    rel_field = fields.Many2one('kw_skill_question_set_config', string="Relation Field")
    active = fields.Boolean(string='Status', default=True,
                            help="The active field allows you to hide the test without removing it.")

    @api.constrains('name', )
    def validate_weightage_name(self):
        if re.match("^[a-zA-Z0-9 ,./()_+-]+$", self.name) == None:
            raise ValidationError("Invalid Question weightage! Please provide a valid weightage Name")

        record = self.env['kw_skill_question_weightage'].search([]) - self
        for info in record:
            if info.name.lower() == self.name.lower():
                raise ValidationError("The weightage Name \"" + self.name + "\" already exists.")

    @api.constrains('code')
    def check_duplicate_code(self):
        for weightage in self:
            if self.env['kw_skill_question_weightage'].search([('code', '=', weightage.code)]) - weightage:
                raise ValidationError(f"Code '{weightage.code}' is already exists.Try a different one.")

    @api.model
    def create(self, vals):
        new_record = super(kw_Question_Weightage, self).create(vals)
        self.env.user.notify_success(message='Question weightage created successfully.')
        return new_record

    @api.multi
    def write(self, vals):
        res = super(kw_Question_Weightage, self).write(vals)
        self.env.user.notify_success(message='Question weightage updated successfully.')
        return res

    @api.multi
    def unlink(self):
        for record in self:
            record.active = False
        return True
