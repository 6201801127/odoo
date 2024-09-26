from odoo import models,fields,api
from odoo.exceptions import ValidationError


class kw_tag_master(models.Model):
    _name = "kw_tag_master"
    _description = "Tag Master"

    name = fields.Char("Title", required=True)
    code = fields.Char("Code", required=True)
    active = fields.Boolean('Active',default=True)
    department_id = fields.Many2one('hr.department', string="Department", domain=[('dept_type.code','=','department')])
    sequence = fields.Integer(
        "Sequence", default=10,
        help="Gives the sequence order of qualification.")

    @api.constrains('name')
    def check_duplicate(self):
        existing = self.env['kw_tag_master'].sudo().search([]) - self
        for record in self:
            for data in existing:
                if record.name.lower() == data.name.lower():
                    raise ValidationError(
                        f"The name {record.name} is already exists.")
                if record.code.lower() == data.code.lower():
                    raise ValidationError(
                        f"The code {record.code} is already exists.")