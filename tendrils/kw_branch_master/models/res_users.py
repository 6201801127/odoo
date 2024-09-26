from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    branch_id = fields.Many2one('kw_res_branch', 'Branch', )
    branch_ids = fields.Many2many('kw_res_branch', id1='user_id', id2='branch_id', string='Branches')
