from odoo import models, fields


class kw_advance_pettycash_exec(models.Model):
    _name = 'kw_advance_pettycash_exec'
    _inherit = ['mail.thread', 'mail.activity.mixin']
