"""
    This is a master class for Card which will be assigned to each employee
"""

from odoo import models, fields


class KWCardMaster(models.Model):
    _name='kw_card_master'
    _description="Master Class for Card"
    _rec_name='name'

    name = fields.Char(string='Card No', required=True)
    description = fields.Text(string='Description', required=True)
    active = fields.Boolean(string='Active', default=True)
    state = fields.Selection([('assigned','Assigned'), ('unassigned','Un-Assigned')], string="Status", default='unassigned')