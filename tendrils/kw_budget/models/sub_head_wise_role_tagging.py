from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SubHeadWiseRoleTagging(models.Model):
    _name = 'sub_head_wise_role_tagging'
    _description = "Sub Head Wise Role tagging"
    _rec_name = 'account_sub_head_id'

    account_sub_head_id = fields.Many2one('account.sub.head', 'Account Sub-Head', required=True)
    role_id = fields.Many2one('kwmaster_role_name', string="Role", required=True)
    category_ids = fields.Many2many('kwmaster_category_name', string="Category", required=True)
    status = fields.Boolean(string="active")

    @api.constrains('account_subhead_id', 'role_id')
    def _check_unique_subhead_role(self):
        for rec in self:
            existing = self.search([
                ('account_sub_head_id', '=', rec.account_sub_head_id.id),
                ('role_id', '=', rec.role_id.id),
                ('id', '!=', rec.id)
            ])
            if existing:
                raise ValidationError('The combination of Account Sub-Head and Role must be unique.')
