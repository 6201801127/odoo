from odoo import api, fields, models, tools, _


class TDS(models.Model):
    _name = "nc.tds"
    _description = "TDS"

    employee_id = fields.Many2one('hr.employee', string='Employee')
    branch_id = fields.Many2one('res.branch','Branch')

