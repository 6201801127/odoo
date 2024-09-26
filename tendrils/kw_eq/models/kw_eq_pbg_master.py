from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class PbgMaster(models.Model):
    _name = 'kw_eq_pbg_master'
    _description = 'PBG Master'

    item = fields.Char(string="Item")
    implementation_percentage = fields.Float(string='Implementation Percentage')
    support_percentage = fields.Float(string='Support Percentage')
    value_edit_bool = fields.Boolean(string="Value Editable")
    percentage_edit_bool = fields.Boolean(string="Percentage Editable")
    code = fields.Char(string="code")
    effective_from = fields.Date(string="Effective Date")




    # @api.depends('write_date')
    # def compute_effective_date(self):
    #     for rec in self:
    #         rec.effective_from = rec.write_date.date()