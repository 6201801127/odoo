from odoo import models, fields


class kw_bonus_master(models.Model):
    _name = 'kw_bonus_master'
    _description = "Bonus Master"

    name = fields.Char(string="Bonus Name")
    amount = fields.Integer(string="Amount")
    new_joinee_id = fields.Many2one('kwonboard_new_joinee')
