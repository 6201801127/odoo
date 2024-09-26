from odoo import models, fields, api


class kw_deduction_line_in(models.Model):
    _inherit = 'kw_advance_deduction_line'

    kw_id = fields.Integer('KW ID')
