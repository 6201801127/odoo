from odoo import models, fields, api


class kw_log_claim_settlement(models.Model):
    _name = 'kw_advance_log_claim_settlement'
    _description = "Petty Cash Settlement log"

    from_user_id = fields.Char(string="From user")
    forwarded_to_user_id = fields.Char(string="To user")
    remark = fields.Char(string="Remark")
