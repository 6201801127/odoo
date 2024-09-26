from unicodedata import category
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class kw_claim_category(models.Model):
    _name = 'kw_advance_claim_category'
    _description = "Claim Category"
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Claim Category", required=True, track_visibility='onchange')
    description = fields.Text(string="Description", track_visibility='onchange')
    sequence = fields.Integer("Sequence", default=0, help="Gives the sequence order of claim category.")
    active = fields.Boolean(string="Active", default=True)
    category = fields.Selection([('advance', 'Advance'), ('claim', 'Claim')], string="Category")
    @api.model
    def create(self, values):
        res = super(kw_claim_category, self).create(values)
        self.env.user.notify_success("Record added successfully.")
        return res

    @api.multi
    def write(self, values):
        res = super(kw_claim_category, self).write(values)
        self.env.user.notify_success("Record updated successfully.")
        if not self.env.user.has_group("kw_advance_claim.group_kw_advance_claim_admin"):
            raise ValidationError(f"""Sorry, you are not allowed to modify this document.You dont have the following access.
                                        1) Advance and claim - Manager access.""")
        return res

    @api.model
    def default_get(self, fields):
        res = super(kw_claim_category, self).default_get(fields)
        if not self.env.user.has_group("kw_advance_claim.group_kw_advance_claim_admin"):
            raise ValidationError(f"""Sorry, you are not allowed to modify this document.You dont have the following access.
                                        1) Advance and claim - Manager access.""")

        return res