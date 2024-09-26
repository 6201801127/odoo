from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class ResUsers(models.Model):
    _inherit = 'res.users'

    # @api.model
    # def create(self, vals):
    #     rec = super(ResUsers, self).create(vals)
    #     if rec:
    #         if rec.has_group('account.group_account_manager') and not rec.has_group('project.group_project_manager'):
    #             raise ValidationError(_(
    #                 'Cannot give access of Chief Accountant if he has access to Project Office'))
    #     return rec
    #
    # def write(self, vals):
    #     rec = super(ResUsers, self).write(vals)
    #     for record in self:
    #         if record.has_group('account.group_account_manager') and not record.has_group('project.group_project_manager'):
    #             raise ValidationError(_(
    #                 'Cannot give access of Chief Accountant if he has access to Project Office'))
    #     return rec
