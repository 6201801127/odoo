import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class kw_skill_score(models.Model):
    _name = 'kw_skill_score_master'
    _description = "A model to create the score Master"

    name = fields.Char(string="Score Name", required=True, size=100)
    code = fields.Char(string="score Code", required=True, size=100)
    min_value = fields.Integer(string="Minimum Value", required=True)
    max_value = fields.Integer(string="Maximum Value", required=True)
    color = fields.Selection(string="color",
                             selection=[('red', 'red'), ('yellow', 'yellow'),
                                        ('green', 'green')], default='red', required=True)
    icon = fields.Char(string="Score Icon", required=True, default=None)
    tagline = fields.Char(string="Tagline", required=True, size=100)
    active = fields.Boolean(string='Status', default=True,
                            help="The active field allows you to hide the test without removing it.")

    @api.constrains('name')
    def validate_skill_score_name(self):
        if re.match("^[a-zA-Z0-9 ,./()_+-]+$", self.name) == None:
            raise ValidationError("Invalid Skill Score! Please provide a valid Skill Score")

        record = self.env['kw_skill_score_master'].search([]) - self
        for info in record:
            if info.name.lower() == self.name.lower():
                raise ValidationError("The Score name \"" + self.name + "\" already exists.")

    @api.constrains('min_value', 'max_value')
    def validate_value(self):
        for record in self:
            if (record.min_value > 100) or (record.min_value < 0):
                raise ValidationError("Value should be greater than 0 and less than 100")
            elif (record.max_value > 100) or (record.max_value < 0):
                raise ValidationError("Value should be greater than 0 and less than 100")

    @api.model
    def create(self, vals):
        new_record = super(kw_skill_score, self).create(vals)
        self.env.user.notify_success(message='Skill Score created successfully.')
        return new_record

    @api.multi
    def write(self, vals):
        res = super(kw_skill_score, self).write(vals)
        self.env.user.notify_success(message='Skill Score updated successfully.')
        return res

    @api.multi
    def unlink(self):
        for record in self:
            record.active = False
        return True
