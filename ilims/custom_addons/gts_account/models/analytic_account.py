from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    allowed_user_ids = fields.Many2many('res.users', string="Visible to", compute='_compute_allowed_user_ids',
                                        store=True, readonly=False, copy=False)

    @api.depends('project_ids', 'project_ids.allowed_user_ids', 'project_ids.privacy_visibility',
                 'project_ids.stakeholder_ids')
    def _compute_allowed_user_ids(self):
        for data in self:
            for record in data.project_ids:
                portal_users = record.allowed_user_ids.filtered('share')
                internal_users = record.allowed_user_ids - portal_users
                if record.privacy_visibility == 'followers':
                    data.allowed_user_ids |= record.allowed_internal_user_ids
                    data.allowed_user_ids -= portal_users
                elif record.privacy_visibility == 'portal':
                    data.allowed_user_ids |= record.allowed_portal_user_ids
                if record.privacy_visibility != 'portal':
                    data.allowed_user_ids -= portal_users
                elif record.privacy_visibility != 'followers':
                    data.allowed_user_ids -= internal_users
