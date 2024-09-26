from odoo import api, fields, models


class Sequence(models.Model):
    _name = "kw_sequence"
    _description = "kw_sequence"
    _rec_name = 'code'

    department_id = fields.Many2one('hr.department', string="Department")
    picking_type_id = fields.Many2one('stock.picking.type', string="Operation Type")
    code = fields.Char(string="Code")
