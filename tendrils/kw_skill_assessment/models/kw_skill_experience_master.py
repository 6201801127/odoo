from odoo import models, fields, api
from odoo.exceptions import ValidationError


class kw_Skill_Experience(models.Model):
    _name = 'kw_skill_experience_master'
    _description = "A model to create skill experience."

    name = fields.Char(string="Title", required=True, size=100)
    min_exp = fields.Integer(string='Minimum Experience (In Years)', default=0, required=True)
    max_exp = fields.Integer(string='Maximum Experience (In Years)', default=0, required=True)
    description = fields.Text(string="Description", )
    active = fields.Boolean(string='Status', default=True,
                            help="The active field allows you to hide the test without removing it.")

    @api.multi
    def unlink(self):
        for record in self:
            record.active = False
        return True
