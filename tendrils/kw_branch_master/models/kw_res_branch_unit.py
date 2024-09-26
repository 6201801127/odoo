from odoo import models, fields, api
from odoo.exceptions import ValidationError


class BranchUnit(models.Model):
    _name = 'kw_res_branch_unit'
    _description = "Res Branch Unit"

    name = fields.Char('Unit Name', required=True)
    address = fields.Text("Address")
    phone_number = fields.Char(string='Phone Number', )
    branch_id = fields.Many2one('kw_res_branch', string='Branch Name', required=True)
    code = fields.Char(string="Alias", required=True)

    active = fields.Boolean('Active', default=True)
    sequence = fields.Integer("Sequence", default=10, help="Gives the sequence.")
