from odoo import models, fields, api


class kw_claim_type(models.Model):
    _name='kw_advance_claim_type'
    _description="Claim type master"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'claim_type'

    claim_type = fields.Char(string="Claim Type",track_visibility='onchange',required=True)
    description = fields.Text(string="Description",track_visibility='onchange')
    claim_category_id = fields.Many2one('kw_advance_claim_category',string="Claim Category",track_visibility='onchange',required=True)
    sequence = fields.Integer(
        "Sequence", default=0,
        help="Gives the sequence order of claim type")
    active = fields.Boolean(string="Active", default=True)

    @api.model
    def create(self, values):
        res = super(kw_claim_type, self).create(values)
        # self.env.user.notify_success("Record added successfully.")
        return res

    
    def write(self, values):
        res = super(kw_claim_type, self).write(values)
        # self.env.user.notify_success("Record updated successfully.")
        return res