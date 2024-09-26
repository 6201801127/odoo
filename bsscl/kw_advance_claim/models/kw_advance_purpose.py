from odoo import models, fields


class kw_advance_purpose(models.Model):
    _name = 'kw_advance_purpose'
    _description = "Advance Purpose"
    _rec_name = 'purpose'
    # _inherit = ['mail.thread', 'mail.activity.mixin']

    purpose = fields.Char(string="Advance Purpose", required=True)
    description = fields.Text(string="Description")
    sequence = fields.Integer("Sequence", default=0, help="Gives the sequence order of purpose.")
    active = fields.Boolean(string="Active", default=True)
    kw_id = fields.Integer("KW ID", default=0, help="Kwantify ID")
