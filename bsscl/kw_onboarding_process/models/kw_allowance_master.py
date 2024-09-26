from odoo import models, fields


class kw_allowance_master(models.Model):
    _name = 'kw_allowance_master'
    _description = "Allowance Master"

    name = fields.Char(string="Allowance Name")
    amount = fields.Integer(string="Amount")
    new_joinee_id = fields.Many2one('kwonboard_new_joinee')
